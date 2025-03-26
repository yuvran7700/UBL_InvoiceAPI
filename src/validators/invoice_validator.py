from fastapi import HTTPException
from datetime import date
from src.models.invoice import Invoice


class InvoiceValidator:
    """
    Validates the business rules of a UBL Invoice.
    Should be called only after required fields are present.
    """

    @classmethod
    def raise_if_invalid(cls, invoice: Invoice) -> None:
        errors = []

        # Issue Date must not be in the future
        if invoice.header.issue_date > date.today():
            errors.append("IssueDate cannot be in the future.")

        # Due Date cannot be before Issue Date
        if (
            invoice.header.due_date
            and invoice.header.due_date < invoice.header.issue_date
        ):
            errors.append("DueDate cannot be earlier than IssueDate.")

        # Validate each invoice line
        for idx, line in enumerate(invoice.invoice_lines, start=1):
            if line.invoiced_quantity <= 0:
                errors.append(f"Invoice Line {idx}: InvoicedQuantity must be positive.")
            if line.price.price_amount < 0:
                errors.append(f"Invoice Line {idx}: PriceAmount cannot be negative.")

            # 4. Validate VAT percentage range
            tax = line.item.classified_tax_category
            if tax and not (0 <= tax.cbc_percent <= 100):
                errors.append(
                    f"Invoice Line {idx}: VAT percent must be between 0 and 100."
                )

        # 5. Validate Total consistency if needed (optional)
        # Example: Check if line_extension_amount is correctly calculated

        # Raise if any errors
        if errors:
            raise HTTPException(status_code=400, detail={"validation_errors": errors})
