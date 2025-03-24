"""
    Strategy context class that orchestrates the construction of an Invoice object from XML or JSON.
"""

from src.marshallers.strategies.order_parsing_strategy import OrderParsingStrategy
from src.models.invoice import Invoice

class InvoiceMarshaller:
    """
    Strategy context class that orchestrates the construction of an Invoice object from XML or JSON.
    """

    def __init__(self, unmarshaller: OrderParsingStrategy):
        self.unmarshaller = unmarshaller

    def marshal(self, content: bytes) -> Invoice:
        """
        Constructs an Invoice object from the provided content.
        This method processes the given binary content to extract and construct
        the necessary components of an invoice, including the header, supplier
        party, customer party, invoice lines, and calculates the total payable
        amount.
        Args:
            content (bytes): The binary content containing invoice data.
        Returns:
            Invoice: An Invoice object populated with the extracted data.
        Raises:
            ValueError: If the content is invalid or required fields are missing.
        """

        header = self.unmarshaller.unmarshal_header(content)

        supplier_party = self.unmarshaller.unmarshal_party(content, "SellerSupplierParty")
        customer_party = self.unmarshaller.unmarshal_party(content, "BuyerCustomerParty")
        invoice_lines = self.unmarshaller.unmarshal_invoice_lines(content)

        # Calculate line extensions
        total = 0
        for line in invoice_lines:
            line.line_extension_amount = line.invoiced_quantity * line.price["price_amount"]
            total += line.line_extension_amount

        return Invoice(
            header=header,
            supplier_party=supplier_party,
            customer_party=customer_party,
            invoice_lines=invoice_lines,
            total={"payable_amount": total}
        )
