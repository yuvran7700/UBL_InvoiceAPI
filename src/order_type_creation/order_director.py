"""
Director for constructing an OrderType object from XML.
Utilizes the OrderXmlExtractor to parse XML and the OrderBuilder to create the final OrderType.
"""

from fastapi import HTTPException
from src.models.order_type import OrderType, OrderLineType
from src.order_type_creation.order_builder import OrderBuilder
from utils.order_xml_extractor import OrderXmlExtractor
from src.models.common.party_attributes import PartyAttributes

class OrderDirector:
    """
    Director class that orchestrates the construction of an OrderType from XML.
    """
    @staticmethod
    def construct_order_from_xml(xml_content: bytes) -> OrderType:
        """
        Constructs an OrderType from the provided XML content.

        Args:
            xml_content (bytes): The XML content of the order.

        Returns:
            OrderType: The constructed order.
        """
        data = OrderXmlExtractor.extract(xml_content)
        builder = OrderBuilder()
        order = (builder
                 .set_order_id(data["header"]["order_reference"])
                 .set_sales_order_id(data["header"]["buyer_reference"])
                 .set_note(data["header"]["note"])
                 .set_buyer(data["buyer"])
                 .set_seller(data["seller"])
                 .set_payment_terms(data["payment_terms"])
                 .set_order_lines([
                     OrderLineType(**line) for line in data["invoice_lines"]
                 ])
                 .build())
        return order
