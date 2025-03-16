"""
Director for constructing an OrderType object from XML.
Uses OrderXmlExtractor to get structured data and OrderBuilder to create the final OrderType.
"""

from fastapi import HTTPException
from src.models.order_type import OrderType, OrderLineType
from order_type_builder import OrderBuilder
from utils.order_xml_extractor import OrderXmlExtractor
from src.models.common.party_attributes import PartyAttributes

class OrderParser:
    @staticmethod
    def parse_xml_order(content: bytes) -> OrderType:
        data = OrderXmlExtractor.extract(content)

        # Build buyer PartyAttributes instance
        buyer_data = data["buyer"]
        buyer = PartyAttributes(
            customer_assigned_account_id=buyer_data["buyer_account_customer_id"],
            supplier_assigned_account_id=buyer_data["buyer_account_supplier_id"],
            party_name=buyer_data["buyer_name"],
            address=buyer_data["buyer_address"],
            endpoint_id=buyer_data["buyer_electronic_address"],
            contact=None,      # Extend if you parse Contact details
            tax_scheme=None    # Extend if you parse TaxScheme details
        )

        # Build seller PartyAttributes instance
        seller_data = data["seller"]
        seller = PartyAttributes(
            customer_assigned_account_id=seller_data["seller_account"],
            supplier_assigned_account_id=seller_data["seller_account"],
            party_name=seller_data["seller_name"],
            address=seller_data["seller_address"],
            endpoint_id=None,
            contact=None,
            tax_scheme=None
        )

        # Convert order line dicts into OrderLineType objects
        order_lines = []
        for line in data["order_lines"]:
            order_line = OrderLineType(
                note=line["note"],
                line_id=line["line_id"],
                quantity=line["quantity"],
                line_extension_amount=line["line_extension_amount"],
                total_tax_amount=line["total_tax_amount"],
                unit_price=line["unit_price"],
                item_description=line["item_description"],
                item_name=line["item_name"],
                buyers_item_id=line["buyers_item_id"],
                sellers_item_id=line["sellers_item_id"],
            )
            order_lines.append(order_line)

        # Use the OrderBuilder to assemble the OrderType product
        builder = OrderBuilder()
        order = (builder
                 .set_order_id(data["header"]["order_id"])
                 .set_sales_order_id(data["header"]["sales_order_id"])
                 .set_issue_date(data["header"]["issue_date"])
                 .set_note(data["header"]["note"])
                 .set_buyer(buyer)
                 .set_seller(seller)
                 .set_anticipated_line_extension_amount(data["monetary"]["anticipated_line_extension_amount"])
                 .set_anticipated_payable_amount(data["monetary"]["anticipated_payable_amount"])
                 .set_payment_terms(data["payment_terms"])
                 .set_order_lines(order_lines)
                 .build())
        return order
