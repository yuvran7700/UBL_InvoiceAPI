"""
Utilities for parsing UBL order documents.
Provides a function to parse an XML order document into an enriched OrderType.
"""

import xml.etree.ElementTree as ET
from fastapi import HTTPException
from models.order_type import OrderType, OrderLineType
from datetime import datetime

class OrderParser:
    """
    OrderParser encapsulates the logic to parse UBL XML order documents.
    """
    @staticmethod
    def get_text(element, path, ns):
        child = element.find(path, ns)
        return child.text.strip() if child is not None and child.text is not None else None

    @staticmethod
    def format_address(address_elem, ns) -> str:
        """
        Formats a postal address by combining available fields.
        """
        if address_elem is None:
            return ""
        street = OrderParser.get_text(address_elem, "./cbc:StreetName", ns) or ""
        building = OrderParser.get_text(address_elem, "./cbc:BuildingNumber", ns) or ""
        city = OrderParser.get_text(address_elem, "./cbc:CityName", ns) or ""
        postal = OrderParser.get_text(address_elem, "./cbc:PostalZone", ns) or ""
        country = OrderParser.get_text(address_elem, "./cac:Country/cbc:IdentificationCode", ns) or ""
        return ", ".join(filter(None, [street, building, city, postal, country]))

    @staticmethod
    def parse_xml_order(content: bytes) -> OrderType:
        """
        Parse an XML UBL order document and extract order information.

        Args:
            content (bytes): The XML file content.

        Returns:
            OrderType: The enriched order data.

        Raises:
            HTTPException: If XML parsing fails or required fields are missing.
        """
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")

        # Define namespaces used in the UBL XML document.
        ns = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        }

        # Extract header fields.
        order_id = OrderParser.get_text(root, "./cbc:ID", ns)
        if not order_id:
            raise HTTPException(status_code=400, detail="Missing order ID in XML")
        sales_order_id = OrderParser.get_text(root, "./cbc:SalesOrderID", ns) or ""
        uuid = OrderParser.get_text(root, "./cbc:UUID", ns) or ""
        issue_date_str = OrderParser.get_text(root, "./cbc:IssueDate", ns)
        if not issue_date_str:
            raise HTTPException(status_code=400, detail="Missing IssueDate in XML")
        try:
            issue_date = datetime.strptime(issue_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid IssueDate format")
        note = OrderParser.get_text(root, "./cbc:Note", ns)

        # Extract buyer details.
        buyer_customer = root.find("./cac:BuyerCustomerParty", ns)
        if buyer_customer is None:
            raise HTTPException(status_code=400, detail="Missing BuyerCustomerParty in XML")
        buyer_account = OrderParser.get_text(buyer_customer, "./cbc:CustomerAssignedAccountID", ns)
        buyer_name = OrderParser.get_text(buyer_customer, ".//cac:PartyName/cbc:Name", ns)
        buyer_address_elem = buyer_customer.find(".//cac:PostalAddress", ns)
        buyer_address = OrderParser.format_address(buyer_address_elem, ns)
        if not buyer_account or not buyer_name:
            raise HTTPException(status_code=400, detail="Missing buyer details in XML")

        # Extract seller details.
        seller_supplier = root.find("./cac:SellerSupplierParty", ns)
        if seller_supplier is None:
            raise HTTPException(status_code=400, detail="Missing SellerSupplierParty in XML")
        seller_account = OrderParser.get_text(seller_supplier, "./cbc:CustomerAssignedAccountID", ns)
        seller_name = OrderParser.get_text(seller_supplier, ".//cac:PartyName/cbc:Name", ns)
        seller_address_elem = seller_supplier.find(".//cac:PostalAddress", ns)
        seller_address = OrderParser.format_address(seller_address_elem, ns)
        if not seller_account or not seller_name:
            raise HTTPException(status_code=400, detail="Missing seller details in XML")

        # Extract monetary totals.
        anticipated_total = root.find("./cac:AnticipatedMonetaryTotal", ns)
        if anticipated_total is None:
            raise HTTPException(status_code=400, detail="Missing AnticipatedMonetaryTotal in XML")
        anticipated_line_extension_amount_str = OrderParser.get_text(anticipated_total, "./cbc:LineExtensionAmount", ns)
        anticipated_payable_amount_str = OrderParser.get_text(anticipated_total, "./cbc:PayableAmount", ns)
        try:
            anticipated_line_extension_amount = float(anticipated_line_extension_amount_str)
            anticipated_payable_amount = float(anticipated_payable_amount_str)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid monetary amounts in XML")

        # Extract payment terms from TransactionConditions.
        transaction_conditions = root.find("./cac:TransactionConditions", ns)
        payment_terms = OrderParser.get_text(transaction_conditions, "./cbc:Description", ns) if transaction_conditions is not None else None

        # Extract order line items.
        order_lines = []
        for order_line_elem in root.findall("./cac:OrderLine", ns):
            line_note = OrderParser.get_text(order_line_elem, "./cbc:Note", ns)
            line_item_elem = order_line_elem.find("./cac:LineItem", ns)
            if line_item_elem is None:
                continue
            line_id = OrderParser.get_text(line_item_elem, "./cbc:ID", ns) or ""
            quantity_str = OrderParser.get_text(line_item_elem, "./cbc:Quantity", ns)
            line_extension_amount_str = OrderParser.get_text(line_item_elem, "./cbc:LineExtensionAmount", ns)
            total_tax_amount_str = OrderParser.get_text(line_item_elem, "./cbc:TotalTaxAmount", ns)
            price_elem = line_item_elem.find("./cac:Price", ns)
            unit_price_str = OrderParser.get_text(price_elem, "./cbc:PriceAmount", ns) if price_elem is not None else None

            item_elem = line_item_elem.find("./cac:Item", ns)
            if item_elem is None:
                continue
            item_description = OrderParser.get_text(item_elem, "./cbc:Description", ns) or ""
            item_name = OrderParser.get_text(item_elem, "./cbc:Name", ns) or ""
            buyers_item_id = OrderParser.get_text(item_elem, "./cac:BuyersItemIdentification/cbc:ID", ns) or ""
            sellers_item_id = OrderParser.get_text(item_elem, "./cac:SellersItemIdentification/cbc:ID", ns) or ""

            try:
                quantity = float(quantity_str) if quantity_str else 0.0
                line_extension_amount = float(line_extension_amount_str) if line_extension_amount_str else 0.0
                total_tax_amount = float(total_tax_amount_str) if total_tax_amount_str else 0.0
                unit_price = float(unit_price_str) if unit_price_str else 0.0
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid numeric value in order line")

            order_line = OrderLineType(
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
            order_lines.append(order_line)

        # Construct and return the enriched OrderType instance.
        return OrderType(
            order_id=order_id,
            sales_order_id=sales_order_id,
            uuid=uuid,
            issue_date=issue_date,
            note=note,
            buyer_account=buyer_account,
            buyer_name=buyer_name,
            buyer_address=buyer_address,
            seller_account=seller_account,
            seller_name=seller_name,
            seller_address=seller_address,
            anticipated_line_extension_amount=anticipated_line_extension_amount,
            anticipated_payable_amount=anticipated_payable_amount,
            payment_terms=payment_terms,
            order_lines=order_lines
        )
