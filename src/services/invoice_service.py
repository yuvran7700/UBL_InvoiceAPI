"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""
from typing import List, Optional
from datetime import date
from nanoid import generate
from fastapi import HTTPException
from src.models.invoice_update import InvoiceUpdateModel
from src.domain.calculators.monetary_calculations import MonetaryCalculator
from src.marshallers.marshaller_factory import MarshallerFactory
from src.models.invoice_response_models import InvoiceResponse, InvoiceStatus
from src.repositories.invoice_repository import get_invoices_by_user, save_invoice, get_invoice_by_id
from src.validators.invoice_validator import InvoiceValidator
from src.validators.missing_field_checker import MissingFieldChecker


class InvoiceService:
    """
    Service layer responsible for orchestrating invoice generation
    from UBL order data.
    """

    def generate_draft_invoice(
        self, content: bytes, file_type: str, user_id: str
    ) -> InvoiceResponse:
        """
        Generates a draft Invoice from the uploaded UBL order data.

        :param content: Raw bytes of the uploaded order file.
        :param file_type: MIME type of the uploaded file (determined by the route).
        :return: Dictionary containing the Invoice and any missing mandatory fields.
        """
        # Select the correct parsing strategy
        invoice = MarshallerFactory().marshal_from_file(content, file_type)

        # Validate required fields
        missing_fields_report = MissingFieldChecker(invoice).run()

        # Generate invoiceID and  assign draft status
        invoice_id = f"INV-{generate(size=8)}"
        invoice.id = invoice_id
        status = InvoiceStatus.DRAFT

        # Store draft in dynamoDB

        save_invoice(invoice, user_id, status)

        return InvoiceResponse(
            invoice_id=invoice_id,
            invoice=invoice,
            missing_fields_report=missing_fields_report,
            status=status
        )

    def complete_invoice(
            self,
            invoice: InvoiceUpdateModel, user_id: str) -> InvoiceResponse:
        """
        Processes a submitted invoice through validation, calculation, and persistence steps.

        :param invoice: Parsed invoice model submitted by the user.
        :param user_id: Identifier of the user submitting the invoice.
        :raises HTTPException: 400 if required fields are missing.
        :return: CompletedInvoiceResponse containing the stored invoice data.
        """

        # Debuggi - print("Populated Invoice Model:\n", invoice.model_dump_json(indent=2))
         # Ensure the invoice has an ID (draft must already exist)
        if not invoice.id:
            raise HTTPException(status_code=400, detail="Cannot complete invoice without an existing ID.")

        # 1. Check for missing fields (pass the model, not the dict)
        missing_report = MissingFieldChecker(invoice).run()

        if missing_report.missing_invoice_fields or missing_report.missing_invoice_lines:
            raise HTTPException(status_code=400, detail=missing_report.dict())

        # 2. Validate mandatory fields and business rules
        InvoiceValidator.raise_if_invalid(invoice)

        # 3. Perform monetary calculations
        # 4. Compute totals using encapsulated logic
        calculator = MonetaryCalculator(invoice)
        calculator.compute_totals()

        # 4. Save the completed invoice (to DynamoDB or DB)
        save_invoice(invoice, user_id, InvoiceStatus.COMPLETED)

        # Return Pydantic response model
        return InvoiceResponse(
            invoice_id=invoice.id,
            invoice=invoice,
            missing_fields_report=None,
            status=InvoiceStatus.COMPLETED
        )



    def get_invoice(self, invoice_id: str, user_id: str) -> InvoiceResponse:
        """
        Retrieves a specific invoice for a given user.

        :param invoice_id: The unique invoice ID.
        :param user_id: The ID of the authenticated user.
        :raises HTTPException: 404 if the invoice does not exist.
        :return: InvoiceResponse with invoice data and status.
        """
        result = get_invoice_by_id(invoice_id, user_id)

        if not result:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        
        invoice, status = result

        # Re-compute missing fields for drafts
        missing_fields_report = (
            MissingFieldChecker(invoice).run()
            if status == InvoiceStatus.DRAFT
            else None
        )

        return InvoiceResponse(
            invoice_id=invoice.id,
            invoice=invoice,
            missing_fields_report = missing_fields_report,
            status=status
        )

    def list_filtered_invoices(
            self,
            user_id: str,
            status: Optional[InvoiceStatus],
            issue_date_from: Optional[date],
            issue_date_to: Optional[date],
        ) -> List[InvoiceResponse]:
        """
        Retrieves all invoices for a given user, applying optional filters.

        Args:
            user_id (str): The user ID requesting the invoices.
            issue_date (Optional[str]): Filter by invoice issue date (YYYY-MM-DD).
            status (Optional[str]): Filter by invoice status.
            invoice_id (Optional[str]): Filter by specific invoice ID.

        Returns:
            List[InvoiceType]: A list of invoices matching the filters.
        """
        # Step 1: Fetch invoices
        invoice_records = get_invoices_by_user(user_id, status)

        # Step 2: Apply filters (date range) here in the service layer
        filtered_responses = []
        for invoice, status_val in invoice_records:
            # Apply issue_date filtering using Pydantic-parsed `date` objects
            if issue_date_from and (not invoice.issue_date or invoice.issue_date < issue_date_from):
                continue
            if issue_date_to and (not invoice.issue_date or invoice.issue_date > issue_date_to):
                continue

            filtered_responses.append(
                InvoiceResponse(
                    invoice_id=invoice.id,
                    invoice=invoice,
                    missing_fields_report=None,
                    status=status_val,
                )
            )

        return filtered_responses
