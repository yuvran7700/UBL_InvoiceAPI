#src/utils/order_xml_extractor.py
"""
Extracts raw order data from a UBL order XML document.
Returns a structured dictionary that includes nested Contact and TaxScheme objects.
"""

from datetime import datetime
import xml.etree.ElementTree as ET
from fastapi import HTTPException
from models.common.contact import Contact
from models.common.tax_scheme import TaxScheme, PartyTaxScheme

class OrderXmlExtractor:
    NAMESPACES = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    @staticmethod
    def get_text(element, path, required=False, error_message=None, ns=None):
        ns = ns or OrderXmlExtractor.NAMESPACES
        child = element.find(path, ns)
        text = child.text.strip() if child is not None and child.text is not None else None
        if required and not text:
            raise HTTPException(
                status_code=400,
                detail=error_message or f"Missing required element: {path}",
            )
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
            raise HTTPException(
                status_code=400, detail=f"Invalid numeric value for {field_name}"
            )

    @staticmethod
    def format_address(address_elem, ns=None) -> str:
        if address_elem is None:
            return ""
        ns = ns or OrderXmlExtractor.NAMESPACES
        parts = [
            OrderXmlExtractor.get_text(address_elem, "./cbc:StreetName", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cbc:BuildingNumber", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cbc:CityName", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cbc:PostalZone", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cbc:CountrySubentity", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cac:AddressLine", ns=ns) or "",
            OrderXmlExtractor.get_text(address_elem, "./cac:Country/cbc:IdentificationCode", ns=ns) or "",
        ]
        return ", ".join(filter(None, parts))

    @staticmethod
    def extract_contact(contact_elem, ns=None):
        """Extracts a Contact object from the given XML element."""
        if contact_elem is None:
            return None
        ns = ns or OrderXmlExtractor.NAMESPACES
        return Contact(
            name=OrderXmlExtractor.get_text(contact_elem, "./cbc:Name", required=True, ns=ns),
            telephone=OrderXmlExtractor.get_text(contact_elem, "./cbc:Telephone", ns=ns),
            telefax=OrderXmlExtractor.get_text(contact_elem, "./cbc:Telefax", ns=ns),
            electronic_mail=OrderXmlExtractor.get_text(contact_elem, "./cbc:ElectronicMail", ns=ns),
        )

    @staticmethod
    def extract_tax_scheme(tax_scheme_elem, ns=None):
        """Extracts a TaxScheme object from the given XML element."""
        if tax_scheme_elem is None:
            return None
        ns = ns or OrderXmlExtractor.NAMESPACES
        return TaxScheme(
            id=OrderXmlExtractor.get_text(tax_scheme_elem, "./cbc:ID", required=True, ns=ns),
            tax_type_code=OrderXmlExtractor.get_text(tax_scheme_elem, "./cbc:TaxTypeCode", ns=ns),
        )

    @staticmethod
    def extract_party_tax_scheme(party_tax_scheme_elem, ns=None):
        """Extracts a PartyTaxScheme object from the given XML element."""
        if party_tax_scheme_elem is None:
            return None
        ns = ns or OrderXmlExtractor.NAMESPACES
        tax_scheme_elem = party_tax_scheme_elem.find("./cac:TaxScheme", ns)
        return PartyTaxScheme(
            registration_name=OrderXmlExtractor.get_text(party_tax_scheme_elem, "./cbc:RegistrationName", ns=ns),
            company_id=OrderXmlExtractor.get_text(party_tax_scheme_elem, "./cbc:CompanyID", required=True, ns=ns),
            exemption_reason=OrderXmlExtractor.get_text(party_tax_scheme_elem, "./cbc:ExemptionReason", ns=ns),
            tax_scheme=OrderXmlExtractor.extract_tax_scheme(tax_scheme_elem, ns)
        )

    @staticmethod
    def extract(xml_content: bytes) -> dict:
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        ns = OrderXmlExtractor.NAMESPACES

        # Header extraction
        header = {
            "order_id": OrderXmlExtractor.get_text(root, "./cbc:ID", required=True, error_message="Missing order ID in XML", ns=ns),
            "sales_order_id": OrderXmlExtractor.get_text(root, "./cbc:SalesOrderID", ns=ns) or "",
            "note": OrderXmlExtractor.get_text(root, "./cbc:Note", ns=ns),
        }

        # Buyer extraction
        buyer_customer = root.find("./cac:BuyerCustomerParty", ns)
        if buyer_customer is None:
            raise HTTPException(status_code=400, detail="Missing BuyerCustomerParty in XML")
        buyer_party = buyer_customer.find("./cac:Party", ns)
        buyer_address_elem = buyer_party.find("./cac:PostalAddress", ns)
        buyer_contact_elem = buyer_party.find("./cac:Contact", ns)
        buyer_tax_scheme_elem = buyer_party.find("./cac:PartyTaxScheme", ns)
        buyer = {
            "buyer_name": OrderXmlExtractor.get_text(buyer_party, ".//cac:PartyName/cbc:Name", required=True, error_message="Missing buyer name in XML", ns=ns),
            "buyer_account_customer_id": OrderXmlExtractor.get_text(buyer_customer, "./cbc:CustomerAssignedAccountID", required=True, error_message="Missing buyer customer account in XML", ns=ns),
            "buyer_account_supplier_id": OrderXmlExtractor.get_text(buyer_customer, "./cbc:SupplierAssignedAccountID", required=True, error_message="Missing buyer supplier account in XML", ns=ns),
            "buyer_address": OrderXmlExtractor.format_address(buyer_address_elem, ns),
            "buyer_electronic_address": OrderXmlExtractor.get_text(buyer_party, "./cac:EndpointID", ns=ns),
            "buyer_scheme_id": (buyer_party.find("./cac:EndpointID", ns).get("schemeID") if buyer_party.find("./cac:EndpointID", ns) is not None else None),
            "buyer_country": (OrderXmlExtractor.get_text(buyer_address_elem, "./cac:Country/cbc:IdentificationCode", ns=ns) if buyer_address_elem is not None else None),
            "buyer_contact": OrderXmlExtractor.extract_contact(buyer_contact_elem, ns),
            "buyer_tax_scheme": OrderXmlExtractor.extract_party_tax_scheme(buyer_tax_scheme_elem, ns),
        }

        # Seller extraction
        seller_supplier = root.find("./cac:SellerSupplierParty", ns)
        if seller_supplier is None:
            raise HTTPException(status_code=400, detail="Missing SellerSupplierParty in XML")
        seller_party = seller_supplier.find("./cac:Party", ns)
        seller_address_elem = seller_party.find("./cac:PostalAddress", ns)
        seller_contact_elem = seller_party.find("./cac:Contact", ns)
        seller_tax_scheme_elem = seller_party.find("./cac:PartyTaxScheme", ns)
        seller = {
            "seller_account": OrderXmlExtractor.get_text(seller_supplier, "./cbc:CustomerAssignedAccountID", required=True, error_message="Missing seller account in XML", ns=ns),
            "seller_name": OrderXmlExtractor.get_text(seller_party, ".//cac:PartyName/cbc:Name", required=True, error_message="Missing seller name in XML", ns=ns),
            "seller_address": OrderXmlExtractor.format_address(seller_address_elem, ns),
            "seller_contact": OrderXmlExtractor.extract_contact(seller_contact_elem, ns),
            "seller_tax_scheme": OrderXmlExtractor.extract_party_tax_scheme(seller_tax_scheme_elem, ns),
        }

        # Monetary totals
        anticipated_total = root.find("./cac:AnticipatedMonetaryTotal", ns)
        if anticipated_total is None:
            raise HTTPException(status_code=400, detail="Missing AnticipatedMonetaryTotal in XML")
        monetary = {
            "anticipated_line_extension_amount": OrderXmlExtractor.parse_float(
                OrderXmlExtractor.get_text(anticipated_total, "./cbc:LineExtensionAmount", required=True, error_message="Missing LineExtensionAmount in XML", ns=ns),
                "LineExtensionAmount"
            ),
            "anticipated_payable_amount": OrderXmlExtractor.parse_float(
                OrderXmlExtractor.get_text(anticipated_total, "./cbc:PayableAmount", required=True, error_message="Missing PayableAmount in XML", ns=ns),
                "PayableAmount"
            ),
        }

        # Payment terms
        transaction_conditions = root.find("./cac:TransactionConditions", ns)
        payment_terms = OrderXmlExtractor.get_text(transaction_conditions, "./cbc:Description", ns=ns) if transaction_conditions is not None else None

        # Order lines
        order_lines = []
        for elem in root.findall("./cac:OrderLine", ns):
            line_note = OrderXmlExtractor.get_text(elem, "./cbc:Note", ns=ns)
            line_item_elem = elem.find("./cac:LineItem", ns)
            if line_item_elem is None:
                continue
            line_id = OrderXmlExtractor.get_text(line_item_elem, "./cbc:ID", ns=ns) or ""
            quantity_str = OrderXmlExtractor.get_text(line_item_elem, "./cbc:Quantity", ns=ns)
            line_extension_str = OrderXmlExtractor.get_text(line_item_elem, "./cbc:LineExtensionAmount", ns=ns)
            tax_amount_str = OrderXmlExtractor.get_text(line_item_elem, "./cbc:TotalTaxAmount", ns=ns)
            price_elem = line_item_elem.find("./cac:Price", ns)
            unit_price_str = (OrderXmlExtractor.get_text(price_elem, "./cbc:PriceAmount", ns=ns) if price_elem is not None else None)
            item_elem = line_item_elem.find("./cac:Item", ns)
            if item_elem is None:
                continue
            item_description = OrderXmlExtractor.get_text(item_elem, "./cbc:Description", ns=ns) or ""
            item_name = OrderXmlExtractor.get_text(item_elem, "./cbc:Name", ns=ns) or ""
            buyers_item_id = OrderXmlExtractor.get_text(item_elem, "./cac:BuyersItemIdentification/cbc:ID", ns=ns) or ""
            sellers_item_id = OrderXmlExtractor.get_text(item_elem, "./cac:SellersItemIdentification/cbc:ID", ns=ns) or ""
            order_line = {
                "note": line_note,
                "line_id": line_id,
                "quantity": OrderXmlExtractor.parse_float(quantity_str, "Quantity"),
                "line_extension_amount": OrderXmlExtractor.parse_float(line_extension_str, "LineExtensionAmount"),
                "total_tax_amount": OrderXmlExtractor.parse_float(tax_amount_str, "TotalTaxAmount"),
                "unit_price": OrderXmlExtractor.parse_float(unit_price_str, "PriceAmount") if unit_price_str else 0.0,
                "item_description": item_description,
                "item_name": item_name,
                "buyers_item_id": buyers_item_id,
                "sellers_item_id": sellers_item_id,
            }
            order_lines.append(order_line)

        return {
            "header": header,
            "buyer": buyer,
            "seller": seller,
            "monetary": monetary,
            "payment_terms": payment_terms,
            "order_lines": order_lines,
        }
