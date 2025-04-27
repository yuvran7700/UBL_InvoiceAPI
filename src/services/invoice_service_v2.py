"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""

from io import BytesIO
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# --- Standard Library ---
from typing import List, Optional, Dict
from datetime import date
from nanoid import generate
# --- Models/Domain Logic ---
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.domain.models.invoice_response_models import InvoiceResponse, InvoiceStatus
from src.domain.calculators.monetary_calculations import MonetaryCalculator
# --- Formatters Logic ---
from src.exceptions.invoice_exceptions import (
    InvoiceCompletionError,
    InvoiceDownloadError,
    InvoiceNotFoundError,
    InvoiceUpdateNotAllowedError
)
from src.marshallers.parsers.marshaller_factory import MarshallerFactory
from src.marshallers.exporters.formatter_factory import FormatterFactory
from src.utils.template_helpers import get_template
# --- Validators Logic ---
from src.validators.invoice_validator import InvoiceValidator
from src.validators.missing_field_checker import MissingFieldChecker
# --- Repository Layers ---
from src.repositories.invoice_repository_v2 import (
    get_invoices_by_organisation,
    save_invoice,
    get_invoice_by_id,
    delete_invoices_by_id
)

class InvoiceService:
    """
    Service layer responsible for orchestrating invoice generation
    from UBL order data.
    """

    def generate_draft_invoice(
        self, content: bytes, file_type: str, organisation_id: str, user_id: str
    ) -> InvoiceResponse:
        invoice = MarshallerFactory().marshal_from_file(content, file_type)

        missing_fields_report = MissingFieldChecker(invoice).run()

        invoice_id = f"INV-{generate(size=8)}"
        invoice.id = invoice_id
        status = InvoiceStatus.DRAFT

        save_invoice(invoice, organisation_id, user_id, status)

        return InvoiceResponse(
            invoice_id=invoice_id,
            invoice=invoice,
            missing_fields_report=missing_fields_report,
            status=status
        )

    def complete_invoice(
        self, invoice: InvoiceUpdateModel, organisation_id: str, user_id: str
    ) -> InvoiceResponse:
        if not invoice.id:
            raise InvoiceCompletionError("Invoice must include an ID to be completed.")

        missing_report = MissingFieldChecker(invoice).run()
        if missing_report.missing_invoice_fields or missing_report.missing_invoice_lines:
            raise InvoiceCompletionError("Invoice has missing required fields.")

        InvoiceValidator.raise_if_invalid(invoice)

        calculator = MonetaryCalculator(invoice)
        calculator.compute_totals()

        save_invoice(invoice, organisation_id, user_id, InvoiceStatus.COMPLETED)

        return InvoiceResponse(
            invoice_id=invoice.id,
            invoice=invoice,
            missing_fields_report=None,
            status=InvoiceStatus.COMPLETED
        )

    def get_invoice(
        self, invoice_id: str, organisation_id: str
    ) -> InvoiceResponse:
        result = get_invoice_by_id(invoice_id, organisation_id)

        if not result:
            raise InvoiceNotFoundError(invoice_id)

        invoice, status = result

        missing_fields_report = (
            MissingFieldChecker(invoice).run()
            if status == InvoiceStatus.DRAFT
            else None
        )

        return InvoiceResponse(
            invoice_id=invoice.id,
            invoice=invoice,
            missing_fields_report=missing_fields_report,
            status=status
        )

    def list_filtered_invoices(
        self,
        organisation_id: str,
        status: Optional[InvoiceStatus] = None,
        issue_date_from: Optional[date] = None,
        issue_date_to: Optional[date] = None,
    ) -> List[InvoiceResponse]:
        
        invoice_records = get_invoices_by_organisation(organisation_id, status)

        filtered_responses = []
        for invoice, status_val in invoice_records:
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

    def delete_user_invoices(
        self, 
        invoice_ids: List[str],
        organisation_id: str,
    ) -> Dict:
        draft_invoices = get_invoices_by_organisation(organisation_id, status=InvoiceStatus.DRAFT)
        draft_invoice_dict = {invoice.id: invoice for invoice, _ in draft_invoices}

        delete_list = []
        errors = []

        for inv_id in invoice_ids:
            if inv_id in draft_invoice_dict:
                delete_list.append(inv_id)
            else:
                errors.append(
                    {"invoice_id": inv_id, "reason": "Invoice not found or not in draft status"}
                )

        if delete_list:
            try:
                delete_invoices_by_id(delete_list, organisation_id)
            except Exception as e:
                errors.append({"invoice_ids": delete_list, "reason": str(e)})

        return {"deleted": delete_list, "errors": errors}

    def update_draft_invoice(
        self,
        invoice_id: str,
        update_data: InvoiceUpdateModel,
        organisation_id: str,
        user_id: str, 
    ) -> InvoiceResponse:
        result = get_invoice_by_id(invoice_id, organisation_id)

        if not result:
            raise InvoiceNotFoundError(invoice_id)

        existing_invoice, current_status = result
        if current_status != InvoiceStatus.DRAFT:
            raise InvoiceUpdateNotAllowedError(invoice_id)

        updated_invoice = existing_invoice.copy(update=update_data.dict(exclude_unset=True))

        missing_fields_report = MissingFieldChecker(updated_invoice).run()

        save_invoice(updated_invoice, organisation_id, user_id, InvoiceStatus.DRAFT) 

        return InvoiceResponse(
            invoice_id=updated_invoice.id,
            invoice=updated_invoice,
            missing_fields_report=missing_fields_report,
            status=InvoiceStatus.DRAFT,
        )


    def generate_invoice_download(
        self, invoice_id: str, format: str, organisation_id: str
    ) -> tuple[bytes, str, str]:
        result = get_invoice_by_id(invoice_id, organisation_id)

        if not result:
            raise InvoiceNotFoundError(invoice_id)

        invoice, status = result

        if status != InvoiceStatus.COMPLETED:
            raise InvoiceDownloadError()

        content = FormatterFactory().serialize(invoice, format)

        media_type = "application/json" if format == "json" else "application/xml"
        filename = f"{invoice.id}.{format}"
        return content, media_type, filename

    def generate_formatted_invoice_download(
        self,
        invoice_id: str,
        organisation_id: str
    ) -> tuple[BytesIO, str]:
        result = get_invoice_by_id(invoice_id, organisation_id)



        if not result:
            raise InvoiceNotFoundError(invoice_id)

        invoice, status = result

        if status != InvoiceStatus.COMPLETED:
            raise InvoiceDownloadError()
        
        tax = invoice.legal_monetary_total.tax_inclusive_amount - invoice.legal_monetary_total.tax_exclusive_amount

        invoice_template = get_template("invoice_template.html")

        html_invoice = invoice_template.render(invoice = invoice, tax = tax)


        content = BytesIO()
        filename = f"{invoice.id}.pdf"
        HTML(string=html_invoice).write_pdf(content)
        content.seek(0)

        return content, filename