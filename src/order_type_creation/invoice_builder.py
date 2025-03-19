"""
Builder for constructing an OrderType object step-by-step.
"""

from datetime import date
from typing import Dict, List, Optional
from src.models.invoice import Contact, Invoice, InvoiceHeader, InvoiceLine, Item, Party, PartyTaxScheme
from src.models.tax import ClassifiedTaxCategoryPatch


class InvoiceBuilder:
    """
    Builder class for constructing an Invoice object with nested models.
    Allows step-by-step construction of an invoice from dynamic extracted data.
    """
    def __init__(self):
        # Initialize attributes for each part of the invoice
        self._invoice_id: Optional[str] = None
        self._issue_date: Optional[date] = None
        self._invoice_type_code: Optional[str] = None
        self._legal_monetary_total: Optional[float] = None
        self._due_date: Optional[date] = None
        self._payment_means: Optional[str] = None
        self._status: Optional[str] = None
        self._order_reference: Optional[str] = None
        self._buyer_reference: Optional[str] = None
        self._note: Optional[str] = None
        self._document_currency_code: Optional[str] = None
        self._invoice_lines: List[InvoiceLine] = []
        
        # Nested objects
        self._supplier_party: Optional[Party] = None
        self._customer_party: Optional[Party] = None
        self._header: Optional[InvoiceHeader] = None

    def set_invoice_id(self, invoice_id: str) -> "InvoiceBuilder":
        self._invoice_id = invoice_id
        return self

    def set_issue_date(self, issue_date: date) -> "InvoiceBuilder":
        self._issue_date = issue_date
        return self

    def set_invoice_type_code(self, invoice_type_code: str) -> "InvoiceBuilder":
        self._invoice_type_code = invoice_type_code
        return self

    def set_legal_monetary_total(self, total_amount: float) -> "InvoiceBuilder":
        self._legal_monetary_total = total_amount
        return self

    def set_due_date(self, due_date: Optional[date]) -> "InvoiceBuilder":
        self._due_date = due_date
        return self

    def set_payment_means(self, payment_means: Optional[str]) -> "InvoiceBuilder":
        self._payment_means = payment_means
        return self

    def set_status(self, status: str) -> "InvoiceBuilder":
        self._status = status
        return self

    def set_order_reference(self, order_reference: str) -> "InvoiceBuilder":
        self._order_reference = order_reference
        return self

    def set_buyer_reference(self, buyer_reference: str) -> "InvoiceBuilder":
        self._buyer_reference = buyer_reference
        return self

    def set_note(self, note: Optional[str]) -> "InvoiceBuilder":
        self._note = note
        return self

    def set_document_currency_code(self, document_currency_code: str) -> "InvoiceBuilder":
        self._document_currency_code = document_currency_code
        return self

    def set_invoice_lines(self, invoice_lines_data: List[Dict]) -> "InvoiceBuilder":
        """
        Dynamically set invoice lines by constructing InvoiceLine objects from extracted data.
        
        Args:
            invoice_lines_data (List[Dict]): The list of raw invoice line data.

        Returns:
            InvoiceBuilder: The builder instance for method chaining.
        """
        self._invoice_lines = []
        for line_data in invoice_lines_data:
            item_data = line_data.get("item", {})
            item = Item(
                name=item_data.get("name"),
                description=item_data.get("description"),
                classified_tax_category=ClassifiedTaxCategoryPatch(**item_data.get("classified_tax_category", {})) if item_data.get("classified_tax_category") else None
            )
            invoice_line = InvoiceLine(
                id=line_data["id"],
                invoiced_quantity=line_data["invoiced_quantity"],
                line_extension_amount=line_data["line_extension_amount"],
                item=item,
                price=line_data.get("price", {})
            )
            self._invoice_lines.append(invoice_line)
        return self

    def _build_party(self, party_data: Dict) -> Party:
        """
        Helper method to build a Party object (supplier or customer) from extracted data.
        
        Args:
            party_data (Dict): The party's raw data (either customer or supplier).

        Returns:
            Party: A constructed Party object.
        """
        return Party(
            endpoint_id=party_data["endpoint_id"],
            party_identification=party_data.get("party_identification", []),
            party_name=party_data["party_name"],
            postal_address=party_data["postal_address"],
            party_legal_entity=party_data["party_legal_entity"],
            contact=Contact(**party_data.get("contact", {})),
            party_tax_scheme=PartyTaxScheme(**party_data.get("party_tax_scheme", {}))
        )

    def set_supplier_party(self, supplier_data: Dict) -> "InvoiceBuilder":
        """
        Set the supplier party by calling the helper function _build_party.
        
        Args:
            supplier_data (Dict): The supplier's raw data.

        Returns:
            InvoiceBuilder: The builder instance for method chaining.
        """
        self._supplier_party = self._build_party(supplier_data)
        return self

    def set_customer_party(self, customer_data: Dict) -> "InvoiceBuilder":
        """
        Set the customer party by calling the helper function _build_party.
        
        Args:
            customer_data (Dict): The customer's raw data.

        Returns:
            InvoiceBuilder: The builder instance for method chaining.
        """
        self._customer_party = self._build_party(customer_data)
        return self

    def set_invoice_header(self, header_data: Dict) -> "InvoiceBuilder":
        """
        Dynamically set the invoice header by constructing InvoiceHeader object from extracted data.
        
        Args:
            header_data (Dict): The header's raw data.

        Returns:
            InvoiceBuilder: The builder instance for method chaining.
        """
        self._header = InvoiceHeader(**header_data)
        return self

    def build(self) -> Invoice:
        """
        Build and return the final Invoice object.
        
        Returns:
            Invoice: The fully constructed invoice object.
        
        Raises:
            ValueError: If any required fields are missing.
        """
        # Ensure that all necessary fields are set
        if not self._invoice_id or not self._issue_date or not self._invoice_type_code or not self._legal_monetary_total:
            raise ValueError("Missing required invoice fields.")
        
        # Return the final Invoice
        return Invoice(
            header=self._header,
            supplier_party=self._supplier_party,
            customer_party=self._customer_party,
            invoice_lines=self._invoice_lines,
            total={"line_extension_amount": self._legal_monetary_total},
        )
