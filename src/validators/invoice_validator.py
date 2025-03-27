from fastapi import HTTPException
from datetime import date
from src.models.invoice_update import InvoiceUpdateModel

class InvoiceValidator:
    """
    Validates the business rules of a UBL Invoice.
    Should be called only after required fields are present.
    """

    @classmethod
    def raise_if_invalid(cls, invoice: InvoiceUpdateModel) -> None:
        errors = []

        # 1. Issue Date must not be in the future
        if invoice.issue_date and invoice.issue_date > date.today():
            errors.append("issue_date cannot be in the future.")

        # 2. Due Date cannot be before Issue Date
        if invoice.due_date and invoice.issue_date:
            if invoice.due_date < invoice.issue_date:
                errors.append("due_date cannot be earlier than issue_date.")

        # 3. Validate each invoice line
        if invoice.invoice_lines:
            for idx, line in enumerate(invoice.invoice_lines, start=1):
                if line.invoiced_quantity is not None and line.invoiced_quantity <= 0:
                    errors.append(f"Line {idx}: invoiced_quantity must be positive.")

                if line.price and line.price.price_amount is not None:
                    if line.price.price_amount < 0:
                        errors.append(f"Line {idx}: price_amount cannot be negative.")

                tax = line.item.classified_tax_category if line.item else None
                if tax and tax.percent is not None:
                    if not (0 <= tax.percent <= 100):
                        errors.append(f"Line {idx}: VAT percent must be between 0 and 100.")

        # 4. Raise if any errors
        if errors:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})
