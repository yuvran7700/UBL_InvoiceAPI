import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Union
from fastapi import HTTPException
from datetime import datetime

from src.domain.models.invoice_update import (
    Party, Address, Contact, PartyTaxScheme, Country,
    InvoicePeriod, OrderReference, InvoiceLine, Item, Price
)
from src.marshallers.parsers.strategies.order_parsing_strategy import OrderParsingStrategy


class XmlOrderParser(OrderParsingStrategy):
    """
    Concrete parsing strategy for UBL XML order documents.
    """

    NAMESPACES = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    def load_data(self, data: Union[bytes, str]) -> ET.Element:
        try:
            return ET.fromstring(data)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")

    def get_text(self, elem, path, required=False) -> Optional[str]:
        target = elem.find(path, self.NAMESPACES)
        if target is not None and target.text:
            return target.text.strip()
        if required:
            raise HTTPException(status_code=400, detail=f"Missing required: {path}")
        return None

    def extract_contact(self, contact_elem) -> Optional[Contact]:
        if contact_elem is None:
            return None
        return Contact(
            name=self.get_text(contact_elem, "./cbc:Name"),
            telephone=self.get_text(contact_elem, "./cbc:Telephone"),
            electronic_mail=self.get_text(contact_elem, "./cbc:ElectronicMail")
        )

    def extract_party_tax_scheme(self, party_tax_scheme_elem) -> Optional[PartyTaxScheme]:
        if party_tax_scheme_elem is None:
            return None
        tax_scheme_elem = party_tax_scheme_elem.find("./cac:TaxScheme", self.NAMESPACES)
        return PartyTaxScheme(
            company_id=self.get_text(party_tax_scheme_elem, "./cbc:CompanyID"),
            tax_scheme_id=self.get_text(tax_scheme_elem, "./cbc:ID") if tax_scheme_elem else None
        )

    def extract_address(self, address_elem) -> Optional[Address]:
        if address_elem is None:
            return None
        country_elem = address_elem.find("./cac:Country", self.NAMESPACES)
        return Address(
            street_name=self.get_text(address_elem, "./cbc:StreetName"),
            additional_street_name=self.get_text(address_elem, "./cbc:AdditionalStreetName"),
            city_name=self.get_text(address_elem, "./cbc:CityName"),
            postal_zone=self.get_text(address_elem, "./cbc:PostalZone"),
            country_subentity=self.get_text(address_elem, "./cbc:CountrySubentity"),
            address_line=self.get_text(address_elem, "./cbc:AddressLine/cbc:Line"),
            country=Country(
                identification_code=self.get_text(country_elem, "./cbc:IdentificationCode")
            ) if country_elem is not None else None
        )

    def extract_party(self, order_data, party_type_elem: str) -> Optional[Party]:
        if not party_type_elem.startswith("cac:"):
            party_type_elem = f"cac:{party_type_elem}"
        party_elem = order_data.find(f".//{party_type_elem}/cac:Party", self.NAMESPACES)

        return Party(
            party_identification=None,
            party_name={"name": self.get_text(party_elem, "./cac:PartyName/cbc:Name")},
            postal_address=self.extract_address(party_elem.find("./cac:PostalAddress", self.NAMESPACES)),
            party_tax_scheme=self.extract_party_tax_scheme(party_elem.find("./cac:PartyTaxScheme", self.NAMESPACES)),
            party_legal_entity=None,
            contact=self.extract_contact(party_elem.find("./cac:Contact", self.NAMESPACES))
        )


    def extract_invoice_period(self, period_elem) -> Optional[InvoicePeriod]:
        if period_elem is None:
            return None
        return InvoicePeriod(
            start_date=self.get_text(period_elem, "./cbc:StartDate"),
            end_date=self.get_text(period_elem, "./cbc:EndDate")
        )

    def extract_order_reference(self, ref_elem) -> Optional[OrderReference]:
        if ref_elem is None:
            return None
        return OrderReference(
            id=self.get_text(ref_elem, "./cbc:ID"),
            sales_order_id=self.get_text(ref_elem, "./cbc:SalesOrderID")
        )

    def extract_item(self, item_elem) -> Optional[Item]:
        if item_elem is None:
            return None
        return Item(
            description=self.get_text(item_elem, "./cbc:Description"),
            name=self.get_text(item_elem, "./cbc:Name"),
            buyers_item_id=self.get_text(item_elem, "./cac:BuyersItemIdentification/cbc:ID"),
            sellers_item_id=self.get_text(item_elem, "./cac:SellersItemIdentification/cbc:ID"),
            standard_item_id=self.get_text(item_elem, "./cac:StandardItemIdentification/cbc:ID"),
            origin_country=None,
            commodity_classification=None,
            classified_tax_category=None
        )

    def extract_invoice_lines(self, lines_data: List[ET.Element]) -> List[InvoiceLine]:
        invoice_lines = []
        for order_line_elem in lines_data:
            line_item_elem = order_line_elem.find("./cac:LineItem", self.NAMESPACES)
            price_elem = line_item_elem.find("./cac:Price", self.NAMESPACES) if line_item_elem is not None else None
            invoice_lines.append(
                InvoiceLine(
                    id=self.get_text(line_item_elem, "./cbc:ID"),
                    invoiced_quantity=float(self.get_text(line_item_elem, "./cbc:Quantity")),
                    item=self.extract_item(line_item_elem.find("./cac:Item", self.NAMESPACES)),
                    price=Price(
                        price_amount=float(self.get_text(price_elem, "./cbc:PriceAmount"))
                    ) if price_elem is not None else None
                )
            )
        return invoice_lines


    def extract_header_fields(self, order_data) -> Dict[str, Optional[Union[str, float]]]:
        return {
            "customization_id": self.get_text(order_data, "./cbc:CustomizationID"),
            "profile_id": self.get_text(order_data, "./cbc:ProfileID"),
            "id": self.get_text(order_data, "./cbc:ID"),
            "issue_date": self.get_text(order_data, "./cbc:IssueDate"),
            "invoice_type_code": "380",
            "document_currency_code": self.get_text(order_data, "./cbc:DocumentCurrencyCode") or "AUD",
            "due_date": self.get_text(order_data, "./cbc:DueDate"),
            "note": self.get_text(order_data, "./cbc:Note"),
            "accounting_cost": self.get_text(order_data, "./cbc:AccountingCost"),
            "buyer_reference": self.get_text(order_data, "./cbc:SalesOrderID"),
        }

    def get_order_lines(self, order_data) -> List[ET.Element]:
        return order_data.findall(".//cac:OrderLine", self.NAMESPACES)