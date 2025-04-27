"""
This module contains a concrete parsing strategy for UBL JSON order documents.
"""

import json
from typing import Dict, List, Optional, Union
from fastapi import HTTPException
from src.domain.models.invoice_update import (
    Party, Address, Contact, PartyLegalEntity, PartyTaxScheme, Country,
    InvoicePeriod, OrderReference, InvoiceLine, Item, Price
)
from src.marshallers.parsers.strategies.order_parsing_strategy import OrderParsingStrategy


class JsonOrderParser(OrderParsingStrategy):
    """
    Concrete parsing strategy for UBL JSON order documents.
    """

    def unwrap(self, value):
        """
        Unwraps a value from a dict if it's a UBL JSON object.

        Args:
            value (Any): The value to unwrap.

        Returns:
            Any: The unwrapped value if the key with an underscore exists,
                    otherwise the original value.
        """
        if isinstance(value, dict) and "_" in value:
            return value["_"]
        return value

    def unwrap_list(self, value):
        """
        Handles unwrapping of lists or dictionaries, returning the first element
         of a list or the dictionary itself if it's not a list.

        Args:
            Aalue (any): The value to unwrap, typically a list or dictionary.

        Returns:
            Any: The first element of the list, the dictionary itself,
             or an empty dictionary if the input is invalid.
        """
        if isinstance(value, list) and value:
            return value[0]
        elif isinstance(value, dict):
            return value  # already unwrapped
        return {}

    def unwrap_and_extract(self, value):
        """
        Combines the functionality of `unwrap` and `unwrap_list` to handle
         nested unwrapping.

        Args:
            value (any): The value to unwrap, typically a nested structure.

        Returns:
            any: The fully unwrapped value.
        """
        val = self.unwrap(self.unwrap_list(value))
        return str(val) if val is not None else None

    def load_data(self, data: bytes) -> dict:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")
        
    def extract_person(self, person_elum) -> Optional[str]:
        if person_elum is None:
            return None
        first_name = self.get_text(person_elum, "./cbc:FirstName") or ""
        last_name = self.get_text(person_elum, "./cbc:FamilyName") or ""
        name_parts = [first_name.strip(), last_name.strip()]
        name = " ".join(part for part in name_parts if part)
        return name

    def extract_contact(self, contact_elem: dict) -> Optional[Contact]:
        if not contact_elem:
            return None
        return Contact(
            name=self.unwrap(contact_elem.get("Name")),
            telephone=self.unwrap(contact_elem.get("Telephone")),
            electronic_mail=self.unwrap(contact_elem.get("ElectronicMail")),
        )
    
    def extract_party_legal_entity(self, party_legal_entity_elem) -> Optional[PartyLegalEntity]:
        if party_legal_entity_elem is None:
            return None
        return PartyLegalEntity(
            registration_name = self.get_text(party_legal_entity_elem, "./cbc:RegistrationName"),
            company_id = self.get_text(party_legal_entity_elem, "./cbc:CompanyID")
    )

    def extract_party_tax_scheme(self, party_tax_scheme_elem) -> Optional[PartyTaxScheme]:
        if not party_tax_scheme_elem:
            return None
        party_tax_scheme_elem = self.unwrap_list(party_tax_scheme_elem)
        return PartyTaxScheme(
            company_id=self.unwrap(party_tax_scheme_elem.get("CompanyID")),
            tax_scheme_id=self.unwrap(party_tax_scheme_elem.get("TaxScheme", {}).get("ID"))
        )

    def extract_address(self, address_elem) -> Optional[Address]:
        if not address_elem:
            return None
        country_elem = address_elem.get("Country", {})

        address_line_elem = self.unwrap_list(address_elem.get("AddressLine"))
        address_line = self.unwrap(address_line_elem.get("Line")) if address_line_elem else None

        return Address(
            street_name=self.unwrap(address_elem.get("StreetName")),
            additional_street_name=self.unwrap(address_elem.get("AdditionalStreetName")),
            city_name=self.unwrap(address_elem.get("CityName")),
            postal_zone=self.unwrap(address_elem.get("PostalZone")),
            country_subentity=self.unwrap(address_elem.get("CountrySubentity")),
            address_line=address_line,
            country=Country(
                identification_code=self.unwrap(country_elem.get("IdentificationCode"))
            ) if country_elem else None
        )

    def extract_party(self, order_data: dict, party_type_elem: str) -> Optional[Party]:
        party_elem = order_data.get("Order", {}).get(party_type_elem, {}).get("Party")
        if not party_elem:
            return None

        party_name_data = self.unwrap_list(party_elem.get("PartyName"))

        return Party(
            party_identification=None,
            party_name={"name": self.unwrap(party_name_data.get("Name"))}
            if party_name_data else None,
            postal_address=self.extract_address(self.unwrap_list(party_elem.get("PostalAddress"))),
            party_tax_scheme=self.extract_party_tax_scheme(party_elem.get("PartyTaxScheme")),
            party_legal_entity=None,  # Optional
            contact=self.extract_contact(party_elem.get("Contact"))
        )

    def extract_invoice_period(self, period_elem: dict) -> Optional[InvoicePeriod]:
        if not period_elem:
            return None
        return InvoicePeriod(
            start_date=self.unwrap(period_elem.get("StartDate")),
            end_date=self.unwrap(period_elem.get("EndDate"))
        )

    def extract_order_reference(self, ref_elem: dict) -> Optional[OrderReference]:
        if not ref_elem:
            return None
        return OrderReference(
            id=self.unwrap(ref_elem.get("ID")),
            sales_order_id=self.unwrap(ref_elem.get("SalesOrderID"))
        )

    def extract_item(self, item_elem: dict) -> Optional[Item]:
        if not item_elem:
            return None
        return Item(
            description=self.unwrap_and_extract(item_elem.get("Description")),
            name=self.unwrap_and_extract(item_elem.get("Name")),
            buyers_item_id=self.unwrap_and_extract(
                item_elem.get("BuyersItemIdentification", {}).get("ID")
            ),
            sellers_item_id=self.unwrap_and_extract(
                item_elem.get("SellersItemIdentification", {}).get("ID")
            ),
            standard_item_id=self.unwrap_and_extract(
                item_elem.get("StandardItemIdentification", {}).get("ID")
            ),
            origin_country=None,
            commodity_classification=None,
            classified_tax_category=None
        )


    def extract_invoice_lines(self, lines_data: List[dict]) -> List[InvoiceLine]:
        invoice_lines = []
        for line in lines_data:
            line_item = line.get("LineItem", {})
            price_elem = line_item.get("Price", {})
            price = Price(
                price_amount=float(self.unwrap_and_extract(price_elem.get("PriceAmount")))
            ) if price_elem else None

            invoice_lines.append(
                InvoiceLine(
                    id=self.unwrap_and_extract(line_item.get("ID")),
                    invoiced_quantity=float(self.unwrap_and_extract(line_item.get("Quantity"))),
                    item=self.extract_item(line_item.get("Item")),
                    price=price
                )
            )
        return invoice_lines


    def extract_header_fields(self, order_data: dict) -> Dict[str, Optional[Union[str, float]]]:
        order_section = order_data.get("Order", {})
        return {
            "customization_id": self.unwrap(order_section.get("CustomizationID")),
            "profile_id": self.unwrap(order_section.get("ProfileID")),
            "id": self.unwrap(order_section.get("ID")),
            "issue_date": self.unwrap(order_section.get("IssueDate")),
            "invoice_type_code": "380",
            "document_currency_code": self.unwrap(order_section.get("DocumentCurrencyCode")) or "AUD",
            "due_date": self.unwrap(order_section.get("DueDate")),
            "note": self.unwrap_and_extract(order_section.get("Note")),  
            "accounting_cost": self.unwrap(order_section.get("AccountingCost")),
            "buyer_reference": self.unwrap(order_section.get("SalesOrderID")),
        }

    def get_order_lines(self, order_data) -> List[dict]:
        return order_data.get("Order", {}).get("OrderLine", [])