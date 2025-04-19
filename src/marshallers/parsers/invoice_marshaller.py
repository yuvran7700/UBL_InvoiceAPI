"""
Strategy context class that orchestrates the construction of an Invoice object from XML or JSON.
"""
from src.domain.models.invoice_update import InvoiceUpdateModel, MonetaryTotal, OrderReference
from src.marshallers.parsers.strategies.order_parsing_strategy import OrderParsingStrategy

class InvoiceMarshaller:
    """
    Service class that builds an InvoiceUpdateModel using the extraction strategy (JSON or XML).
    """

    def __init__(self, extractor: OrderParsingStrategy):
        self.extractor = extractor

    def marshal(self, content: bytes) -> InvoiceUpdateModel:
        """
        Constructs the InvoiceUpdateModel from extracted raw data.
        """
        order_data = self.extractor.load_data(content)

        # Extract components
        header_data = self.extractor.extract_header_fields(order_data)
        supplier_party = self.extractor.extract_party(order_data, "SellerSupplierParty")
        customer_party = self.extractor.extract_party(order_data, "BuyerCustomerParty")

        order_lines_data = self.extractor.get_order_lines(order_data)
        invoice_lines = self.extractor.extract_invoice_lines(order_lines_data)


        # Compute line extension total
        line_extension_total = 0
        for line in invoice_lines:
            if line.invoiced_quantity and line.price and line.price.price_amount:
                line.line_extension_amount = line.invoiced_quantity * line.price.price_amount
                line_extension_total += line.line_extension_amount

        # Assemble monetary totals
        legal_monetary_total = MonetaryTotal(
            line_extension_amount=line_extension_total,
            tax_exclusive_amount=None,  # Optional to extend
            tax_inclusive_amount=None,
            payable_amount=None
        )

        # Build InvoiceUpdateModel with snake_case fields
        invoice = InvoiceUpdateModel(
            customization_id=header_data.get("customization_id"),
            profile_id=header_data.get("profile_id"),
            id=header_data.get("id"),
            issue_date=header_data.get("issue_date"),
            invoice_type_code=header_data.get("invoice_type_code"),
            document_currency_code=header_data.get("document_currency_code"),
            due_date=header_data.get("due_date"),
            note=header_data.get("note"),
            accounting_cost=header_data.get("accounting_cost"),
            buyer_reference=header_data.get("buyer_reference"),

            accounting_supplier_party=supplier_party,
            accounting_customer_party=customer_party,
            invoice_lines=invoice_lines,
            legal_monetary_total=legal_monetary_total,

            # Optional / Extendable
            order_reference=OrderReference(id=header_data.get("id")) if header_data.get("id") else None
        )

        return invoice
