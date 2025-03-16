#src/order_type_builder/order_director.py
"""
Director for constructing an OrderType object from XML.
Uses OrderXmlExtractor to get structured data and OrderBuilder to create the final OrderType.
"""

from fastapi import HTTPException
from src.models.order_type import OrderType, OrderLineType
from src.order_type_builder.order_builder import OrderBuilder
from utils.order_xml_extractor import OrderXmlExtractor
from src.models.common.party_attributes import PartyAttributes

class OrderDirector:
    @staticmethod
    def construct_order_from_xml(xml_content: bytes) -> OrderType:
        # Extract data from XML
        data = OrderXmlExtractor.extract(xml_content)

        # Use OrderBuilder to construct the OrderType
        builder = OrderBuilder()
        order = (builder
                 .set_order_id(data["header"]["order_id"])
                 .set_sales_order_id(data["header"]["sales_order_id"])
                 .set_issue_date(data["header"]["issue_date"])
                 .set_note(data["header"]["note"])
                 .set_buyer(data["buyer"])  # Pass buyer data as a dictionary
                 .set_seller(data["seller"])  # Pass seller data as a dictionary
                 .set_anticipated_line_extension_amount(data["monetary"]["anticipated_line_extension_amount"])
                 .set_anticipated_payable_amount(data["monetary"]["anticipated_payable_amount"])
                 .set_payment_terms(data["payment_terms"])
                 .set_order_lines([
                     OrderLineType(**line) for line in data["order_lines"]
                 ])
                 .build())
        return order