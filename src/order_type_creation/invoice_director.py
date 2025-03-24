"""
Director for constructing an OrderType object from XML.
Utilizes the OrderXmlExtractor to parse XML and the OrderBuilder to create the final OrderType.
"""

from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller
from src.models.invoice import Invoice
from src.order_type_creation.invoice_builder import InvoiceBuilder
from fastapi import HTTPException
import json
import xml.etree.ElementTree as ET

class InvoiceDirector:
    """
    Director class that orchestrates the construction of an Invoice object from XML or JSON.
    """

    def __init__(self, unmarshaller: OrderUnmarshaller):
        self.unmarshaller = unmarshaller

    def construct_invoice_from_data(self, content: bytes) -> Invoice:
        header = self.unmarshaller.unmarshal_header(content)
        supplier_party = self.unmarshaller.unmarshal_party(content, "cac:SellerSupplierParty")
        customer_party = self.unmarshaller.unmarshal_party(content, "cac:BuyerCustomerParty")
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