# src/calculators/monetary_calculations.py

from src.models.invoice_update import InvoiceUpdateModel

class MonetaryCalculator:
    """
    Encapsulates monetary calculation logic for invoices.
    Calculates totals and mutates the given InvoiceUpdateModel.
    """

    def __init__(self, invoice: InvoiceUpdateModel):
        self.invoice = invoice

    def compute_totals(self) -> None:
        """
        Calculates tax-exclusive, tax-inclusive, and payable amounts.
        Updates the invoice in-place.
        """
        legal = self.invoice.legal_monetary_total
        line_extension_total = legal.line_extension_amount
        total_tax = 0.0

        for line in self.invoice.invoice_lines:
            tax = self._calculate_tax_for_line(line)
            total_tax += tax

        legal.tax_exclusive_amount = line_extension_total
        legal.tax_inclusive_amount = line_extension_total + total_tax
        legal.payable_amount = legal.tax_inclusive_amount

    def _calculate_tax_for_line(self, line) -> float:
        tax_category = line.item.classified_tax_category
        if tax_category and tax_category.percent is not None:
            tax_rate = tax_category.percent / 100
            return line.line_extension_amount * tax_rate
        return 0.0
