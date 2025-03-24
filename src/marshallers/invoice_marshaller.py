"""
    InvoiceMarshaller is responsible for extracting structured data from 
    raw UBL order content (XML or JSON) and assembling it into the Invoice
    domain model.
"""

from src.marshallers.strategies.order_parsing_strategy import OrderParsingStrategy
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller
from src.models.invoice import Invoice

class InvoiceMarshaller:
    """
    Director class that orchestrates the construction of an Invoice object from XML or JSON.
    """

    def __init__(self, unmarshaller: OrderParsingStrategy):
        self.unmarshaller = unmarshaller

    def construct_invoice_from_data(self, content: bytes) -> Invoice:
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