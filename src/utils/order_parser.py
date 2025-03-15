#utils/order_parser.py
"""
Utilities for parsing UBL order documents.
Provides a function to parse an XML order document into an enriched OrderType.
"""

import xml.etree.ElementTree as ET
from fastapi import HTTPException
from src.models.order_type import OrderType, OrderLineType
from datetime import datetime

class OrderParser:
    # Define XML namespaces as a class constant
    NAMESPACES = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
    }
    
    @staticmethod
    def get_text(element, path, required=False, error_message=None, ns=None):
        ns = ns or OrderParser.NAMESPACES
        child = element.find(path, ns)
        text = child.text.strip() if child is not None and child.text is not None else None
        if required and not text:
            raise HTTPException(status_code=400, detail=error_message or f"Missing required element: {path}")
        return text

    @staticmethod
    def parse_date(text, field_name):
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid {field_name} format")

    @staticmethod
    def parse_float(text, field_name):
        try:
            return float(text)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail=f"Invalid numeric value for {field_name}")

    @staticmethod
    def format_address(address_elem, ns=None) -> str:
        if address_elem is None:
            return ""
        ns = ns or OrderParser.NAMESPACES
        parts = [
            OrderParser.get_text(address_elem, "./cbc:StreetName", ns=ns) or "",
            OrderParser.get_text(address_elem, "./cbc:BuildingNumber", ns=ns) or "",
            OrderParser.get_text(address_elem, "./cbc:CityName", ns=ns) or "",
            OrderParser.get_text(address_elem, "./cbc:PostalZone", ns=ns) or "",
            OrderParser.get_text(address_elem, "./cac:Country/cbc:IdentificationCode", ns=ns) or ""
        ]
        return ", ".join(filter(None, parts))
    
    @staticmethod
    def parse_order_header(root, ns):
        order_id = OrderParser.get_text(
            root, "./cbc:ID", required=True,
            error_message="Missing order ID in XML", ns=ns
        )
        sales_order_id = OrderParser.get_text(root, "./cbc:SalesOrderID", ns=ns) or ""
        issue_date_str = OrderParser.get_text(
            root, "./cbc:IssueDate", required=True,
            error_message="Missing IssueDate in XML", ns=ns
        )
        issue_date = OrderParser.parse_date(issue_date_str, "IssueDate")
        note = OrderParser.get_text(root, "./cbc:Note", ns=ns)
        return {
            "order_id": order_id,
            "sales_order_id": sales_order_id,
            "issue_date": issue_date,
            "note": note
        }

    @staticmethod
    def parse_buyer_details(root, ns):
        buyer_customer = root.find("./cac:BuyerCustomerParty", ns)
        if buyer_customer is None:
            raise HTTPException(status_code=400, detail="Missing BuyerCustomerParty in XML")
        buyer_name = OrderParser.get_text(
            buyer_customer, ".//cac:PartyName/cbc:Name", required=True,
            error_message="Missing buyer name in XML", ns=ns
        )
        buyer_account = OrderParser.get_text(
            buyer_customer, "./cbc:CustomerAssignedAccountID", required=True,
            error_message="Missing buyer account in XML", ns=ns
        )
        buyer_address_elem = buyer_customer.find(".//cac:PostalAddress", ns)
        buyer_address = OrderParser.format_address(buyer_address_elem, ns)
        buyer_electronic_address = OrderParser.get_text(buyer_customer, "./cac:Party/cbc:EndpointID", ns=ns)
        buyer_scheme_id = None
        if buyer_electronic_address:
            endpoint = buyer_customer.find("./cac:Party/cbc:EndpointID", ns)
            buyer_scheme_id = endpoint.get("schemeID") if endpoint is not None else None
        buyer_country = (OrderParser.get_text(buyer_address_elem, "./cac:Country/cbc:IdentificationCode", ns=ns)
                         if buyer_address_elem is not None else None)
        return {
            "buyer_name": buyer_name,
            "buyer_account": buyer_account,
            "buyer_address": buyer_address,
            "buyer_electronic_address": buyer_electronic_address,
            "buyer_scheme_id": buyer_scheme_id,
            "buyer_country": buyer_country
        }

    @staticmethod
    def parse_seller_details(root, ns):
        seller_supplier = root.find("./cac:SellerSupplierParty", ns)
        if seller_supplier is None:
            raise HTTPException(status_code=400, detail="Missing SellerSupplierParty in XML")
        seller_account = OrderParser.get_text(
            seller_supplier, "./cbc:CustomerAssignedAccountID", required=True,
            error_message="Missing seller account in XML", ns=ns
        )
        seller_name = OrderParser.get_text(
            seller_supplier, ".//cac:PartyName/cbc:Name", required=True,
            error_message="Missing seller name in XML", ns=ns
        )
        seller_address_elem = seller_supplier.find(".//cac:PostalAddress", ns)
        seller_address = OrderParser.format_address(seller_address_elem, ns)
        return {
            "seller_account": seller_account,
            "seller_name": seller_name,
            "seller_address": seller_address
        }

    @staticmethod
    def parse_monetary_totals(root, ns):
        anticipated_total = root.find("./cac:AnticipatedMonetaryTotal", ns)
        if anticipated_total is None:
            raise HTTPException(status_code=400, detail="Missing AnticipatedMonetaryTotal in XML")
        line_ext_str = OrderParser.get_text(
            anticipated_total, "./cbc:LineExtensionAmount", required=True,
            error_message="Missing LineExtensionAmount in XML", ns=ns
        )
        payable_str = OrderParser.get_text(
            anticipated_total, "./cbc:PayableAmount", required=True,
            error_message="Missing PayableAmount in XML", ns=ns
        )
        return {
            "anticipated_line_extension_amount": OrderParser.parse_float(line_ext_str, "LineExtensionAmount"),
            "anticipated_payable_amount": OrderParser.parse_float(payable_str, "PayableAmount")
        }

    @staticmethod
    def parse_payment_terms(root, ns):
        transaction_conditions = root.find("./cac:TransactionConditions", ns)
        return (OrderParser.get_text(transaction_conditions, "./cbc:Description", ns=ns)
                if transaction_conditions is not None else None)

    @staticmethod
    def parse_order_line(order_line_elem, ns):
        line_note = OrderParser.get_text(order_line_elem, "./cbc:Note", ns=ns)
        line_item_elem = order_line_elem.find("./cac:LineItem", ns)
        if line_item_elem is None:
            return None
        line_id = OrderParser.get_text(line_item_elem, "./cbc:ID", ns=ns) or ""
        quantity_str = OrderParser.get_text(line_item_elem, "./cbc:Quantity", ns=ns)
        line_extension_str = OrderParser.get_text(line_item_elem, "./cbc:LineExtensionAmount", ns=ns)
        tax_amount_str = OrderParser.get_text(line_item_elem, "./cbc:TotalTaxAmount", ns=ns)
        price_elem = line_item_elem.find("./cac:Price", ns)
        unit_price_str = OrderParser.get_text(price_elem, "./cbc:PriceAmount", ns=ns) if price_elem is not None else None

        item_elem = line_item_elem.find("./cac:Item", ns)
        if item_elem is None:
            return None
        item_description = OrderParser.get_text(item_elem, "./cbc:Description", ns=ns) or ""
        item_name = OrderParser.get_text(item_elem, "./cbc:Name", ns=ns) or ""
        buyers_item_id = OrderParser.get_text(item_elem, "./cac:BuyersItemIdentification/cbc:ID", ns=ns) or ""
        sellers_item_id = OrderParser.get_text(item_elem, "./cac:SellersItemIdentification/cbc:ID", ns=ns) or ""

        quantity = OrderParser.parse_float(quantity_str, "Quantity")
        line_extension_amount = OrderParser.parse_float(line_extension_str, "LineExtensionAmount")
        total_tax_amount = OrderParser.parse_float(tax_amount_str, "TotalTaxAmount")
        unit_price = OrderParser.parse_float(unit_price_str, "PriceAmount") if unit_price_str else 0.0

        return OrderLineType(
            note=line_note,
            line_id=line_id,
            quantity=quantity,
            line_extension_amount=line_extension_amount,
            total_tax_amount=total_tax_amount,
            unit_price=unit_price,
            item_description=item_description,
            item_name=item_name,
            buyers_item_id=buyers_item_id,
            sellers_item_id=sellers_item_id
        )

    @staticmethod
    def parse_order_lines(root, ns):
        return [
            line for line in (
                OrderParser.parse_order_line(elem, ns)
                for elem in root.findall("./cac:OrderLine", ns)
            ) if line is not None
        ]

    @staticmethod
    def parse_xml_order(content: bytes) -> OrderType:
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        
        ns = OrderParser.NAMESPACES
        header = OrderParser.parse_order_header(root, ns)
        buyer = OrderParser.parse_buyer_details(root, ns)
        seller = OrderParser.parse_seller_details(root, ns)
        monetary = OrderParser.parse_monetary_totals(root, ns)
        payment_terms = OrderParser.parse_payment_terms(root, ns)
        order_lines = OrderParser.parse_order_lines(root, ns)

        return OrderType(
            order_id=header["order_id"],
            sales_order_id=header["sales_order_id"],
            issue_date=header["issue_date"],
            note=header["note"],
            buyer_account=buyer["buyer_account"],
            buyer_name=buyer["buyer_name"],
            buyer_address=buyer["buyer_address"],
            seller_account=seller["seller_account"],
            seller_name=seller["seller_name"],
            seller_address=seller["seller_address"],
            anticipated_line_extension_amount=monetary["anticipated_line_extension_amount"],
            anticipated_payable_amount=monetary["anticipated_payable_amount"],
            payment_terms=payment_terms,
            order_lines=order_lines
        )