"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""
from typing import List, Optional, Dict
from datetime import date
from nanoid import generate
# --- Models/Domain Logic ---
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.domain.models.invoice_response_models import InvoiceResponse, InvoiceStatus
from src.domain.calculators.monetary_calculations import MonetaryCalculator
# --- Formatters Logic ---
from src.exceptions.invoice_exceptions import InvoiceCompletionError, InvoiceDownloadError, InvoiceNotFoundError, InvoiceUpdateNotAllowedError
from src.marshallers.parsers.marshaller_factory import MarshallerFactory
from src.marshallers.exporters.formatter_factory import FormatterFactory
# --- Validators Logic ---
from src.validators.invoice_validator import InvoiceValidator
from src.validators.missing_field_checker import MissingFieldChecker
# --- Repository Layers ---
from src.repositories.invoice_repository import get_invoices_by_user, save_invoice, get_invoice_by_id, delete_invoices_by_id


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
            raise InvoiceCompletionError("Invoice must include an ID to be completed.")

        # 1. Check for missing fields (pass the model, not the dict)
        missing_report = MissingFieldChecker(invoice).run()


        if missing_report.missing_invoice_fields or missing_report.missing_invoice_lines:
            raise InvoiceCompletionError("Invoice has missing required fields.")

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
            raise InvoiceNotFoundError(invoice_id)

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

    def delete_user_invoices(self, invoice_ids: List[str], user_id: str) -> Dict:
        """
        Deletes multiple invoices for a given user.
        Uses the list_invoices repository function to pre-validate that each invoice:
          - Exists, and
          - Is in draft status.
        Then, deletes all validated invoices in a single batch call.
        Returns a summary dict containing:
          - "deleted": list of successfully deleted invoice IDs
          - "errors": list of dictionaries with invoice_id and failure reason.
        """
        # Step 1: Fetch all draft invoices for the user.
        draft_invoices = get_invoices_by_user(user_id, status=InvoiceStatus.DRAFT)
        # Convert the tuple list to a dictionary keyed by invoice ID.
        draft_invoice_dict = {invoice.id: invoice for invoice, _ in draft_invoices}

        # Debug: print("\n[DEBUG] Draft Invoice Dictionary:", draft_invoice_dict)

        delete_list = []
        errors = []

        # Step 2: Validate provided invoice_ids against the draft invoices.
        for inv_id in invoice_ids:
            if inv_id in draft_invoice_dict:
                delete_list.append(inv_id)
            else:
                errors.append(
                    {"invoice_id": inv_id, "reason": "Invoice not found or not in draft status"})

        # Step 3: Batch delete the validated invoice IDs.
        if delete_list:
            try:
                delete_invoices_by_id(delete_list, user_id)
            except Exception as e:
                errors.append({"invoice_ids": delete_list, "reason": str(e)})

        return {"deleted": delete_list, "errors": errors}

    def update_draft_invoice(
            self,
            invoice_id: str,
            update_data: InvoiceUpdateModel,
            user_id: str
            ) -> InvoiceResponse:
        """"
            Docstring To be Added
        """
        # Retrieve the existing draft invoice.
        result = get_invoice_by_id(invoice_id, user_id)
        if not result:
            raise InvoiceNotFoundError(invoice_id)

        existing_invoice, current_status = result
        if current_status != InvoiceStatus.DRAFT:
            raise InvoiceUpdateNotAllowedError(invoice_id)

        # Merge the update into the existing invoice.
        updated_invoice = existing_invoice.copy(update=update_data.dict(exclude_unset=True))

        # Re-run the missing fields check.
        missing_fields_report = MissingFieldChecker(updated_invoice).run()


        # Save the updated draft invoice.
        save_invoice(updated_invoice, user_id, InvoiceStatus.DRAFT)

        # Return the updated invoice with missing fields report.
        return InvoiceResponse(
            invoice_id=updated_invoice.id,
            invoice=updated_invoice,
            missing_fields_report=missing_fields_report,
            status=InvoiceStatus.DRAFT
        )

    def generate_invoice_download(self, invoice_id: str, format: str, user_id: str) -> tuple[bytes, str, str]:
        result = get_invoice_by_id(invoice_id, user_id)

        if not result:
            raise InvoiceNotFoundError(invoice_id)
        
        invoice, status = result

        if status != InvoiceStatus.COMPLETED:
            raise InvoiceDownloadError()

        content = FormatterFactory().serialize(invoice, format)

        media_type = "application/json" if format == "json" else "application/xml"
        filename = f"{invoice.id}.{format}"
        return content, media_type, filename
