"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""

from typing import Dict, List
from fastapi import HTTPException
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.models.invoice_response_models import CompletedInvoiceResponse, DraftInvoiceResponse
from src.models.invoice_update import InvoiceUpdateModel
from src.repositories.invoice_repository import save_invoice
from src.validators.invoice_validator import InvoiceValidator
from src.validators.missing_field_checker import MissingFieldChecker


class InvoiceService:
    """
    Service layer responsible for orchestrating invoice generation
    from UBL order data.
    """

    def generate_draft_invoice(
        self, content: bytes, file_type: str, user_id: str
    ) -> DraftInvoiceResponse:
        """
        Generates a draft Invoice from the uploaded UBL order data.

        :param content: Raw bytes of the uploaded order file.
        :param file_type: MIME type of the uploaded file (determined by the route).
        :return: Dictionary containing the Invoice and any missing mandatory fields.
        """
        # Select the correct parsing strategy
        parser = self._select_parsing_strategy(file_type)

        # Assemble the Invoice using the marshaller
        assembler = InvoiceMarshaller(parser)
        invoice: InvoiceUpdateModel = assembler.marshal(content)

        # Validate required fields
        missing_fields_report = MissingFieldChecker(invoice).run()


        # TODO: attach user_id, or store draft
        # self._save_draft(user_id, invoice)

        return DraftInvoiceResponse(
        invoice=invoice.dict(exclude_none=True),
        missing_fields_report=missing_fields_report
        )

    def _select_parsing_strategy(self, file_type: str):
        """
        Determines the appropriate parser based on file MIME type.

        :param file_type: MIME type of the uploaded file.
        :return: Instance of a concrete parsing strategy.
        """
        if "xml" in file_type:
            return XmlOrderParser()
        elif "json" in file_type:
            return JsonOrderParser()
        else:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Only XML and JSON are supported.",
            )

    def complete_invoice(self, invoice: InvoiceUpdateModel, user_id: str) -> CompletedInvoiceResponse:

        # Debugging Purposes - print("Populated Invoice Model:\n", invoice.model_dump_json(indent=2))

        # 1. Check for missing fields (pass the model, not the dict)
        missing_report = MissingFieldChecker(invoice).run()
        
        if missing_report.missing_invoice_fields or missing_report.missing_invoice_lines:
            raise HTTPException(status_code=400, detail=missing_report.model_dump())

        # 2. Validate mandatory fields and business rules
        InvoiceValidator.raise_if_invalid(invoice)

        # 3. Perform monetary calculations
        self._compute_legal_monetary_totals(invoice)

        # 4. Save the completed invoice (to DynamoDB or DB)
        save_invoice(invoice, user_id)

        # Return Pydantic response model
        return CompletedInvoiceResponse(
            invoice_id=invoice.id,
            invoice=invoice
        )


    def _compute_legal_monetary_totals(self, invoice: InvoiceUpdateModel):
        line_extension_total = invoice.legal_monetary_total.line_extension_amount
        total_tax_amount = 0.0

        for line in invoice.invoice_lines:
            tax_category = line.item.classified_tax_category
            if tax_category and tax_category.cbc_percent is not None:
                tax_rate = tax_category.cbc_percent / 100
                tax_amount = line.line_extension_amount * tax_rate
                total_tax_amount += tax_amount

        invoice.legal_monetary_total.tax_exclusive_amount = line_extension_total
        invoice.legal_monetary_total.tax_inclusive_amount = line_extension_total + total_tax_amount
        invoice.legal_monetary_total.payable_amount = invoice.legal_monetary_total.tax_inclusive_amount
