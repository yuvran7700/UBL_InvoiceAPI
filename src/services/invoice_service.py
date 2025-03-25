"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""

from fastapi import HTTPException
from typing import Dict, List
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.utils.missing_field_checker import find_missing_fields
from src.validators.invoice_validator import InvoiceValidator
from src.repositories.invoice_repository import save_invoice
from src.models.invoice import Invoice

class InvoiceService:
    """
    Service layer responsible for orchestrating invoice generation
    from UBL order data.
    """

    def generate_draft_invoice(self, content: bytes, file_type: str, user_id: str) -> dict:
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
        invoice: Invoice = assembler.marshal(content)

        # Validate required fields
        missing_fields = find_missing_fields(invoice)
        
        # TODO: attach user_id, or store draft
        # self._save_draft(user_id, invoice)

        return {
            "invoice": invoice,
            "missing_fields": missing_fields
        }

    def _select_parsing_strategy(self, file_type: str):
        """
        Determines the appropriate parser based on file MIME type.

        :param file_type: MIME type of the uploaded file.
        :return: Instance of a concrete parsing strategy.
        """
        if file_type == "application/xml":
            return XmlOrderParser()
        elif file_type == "application/json":
            return JsonOrderParser()
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type. Only XML and JSON are supported.")

    def complete_invoice(self, invoice_data: dict, user_id: str) -> dict:
        # Convert dict to Invoice model
        invoice = Invoice(**invoice_data)
        
        # Debugging Purposes
        print("Populated Invoice Model:\n", invoice.model_dump_json(indent=2))


        missing_fields = find_missing_fields(invoice)
        if missing_fields:
            # Return early to frontend if incomplete
            raise HTTPException(
                status_code=400,
                detail={"missing_fields": missing_fields}
            )
    
        # 1. Validate mandatory fields and business rules
        InvoiceValidator.raise_if_invalid(invoice)

        # 2. Perform legal calculations
        self._compute_legal_monetary_totals(invoice)

        # (Optional) Compute Tax Total if needed
        # tax_total = self._calculate_tax(invoice.invoice_lines)

        # 4. Save the completed invoice (to DynamoDB or DB)
        save_invoice(invoice, user_id)

        return {"invoice_id": invoice.header.invoice_id, "invoice": invoice}

    def _compute_legal_monetary_totals(self, invoice: Invoice):
        # Use the already populated line_extension_amount from marshaller
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