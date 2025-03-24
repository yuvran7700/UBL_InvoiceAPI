"""
This module contains a concrete parsing strategy for UBL JSON order documents.
"""

import json
from typing import List, Optional
from fastapi import HTTPException
from src.models.invoice import Contact, InvoiceLine, Item, Party, PartyTaxScheme, InvoiceHeader
from src.models.tax import TaxScheme
from src.marshallers.strategies.order_parsing_strategy import OrderParsingStrategy


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
        return self.unwrap(self.unwrap_list(value))
  
    def load_json(self, data: bytes) -> dict:
        """
        Loads JSON data from a byte string and returns a dictionary.
        
        Args:
            data (bytes): The JSON data as a byte string.

        Returns:
            dict: The parsed JSON object.

        Raises:
            HTTPException: If the JSON data is invalid or cannot be parsed.
        """
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")

    def extract_contact(self, contact_elem, ns=None) -> Optional[Contact]:
        if not contact_elem:
            return None

        return Contact(
            name=self.unwrap(contact_elem.get("Name")),
            telephone=self.unwrap(contact_elem.get("Telephone")),
            telefax=self.unwrap(contact_elem.get("Telefax")),
            electronic_mail=self.unwrap(contact_elem.get("ElectronicMail")),
        )

    def extract_tax_scheme(self, tax_scheme_elem, ns=None) -> Optional[TaxScheme]:
        if not tax_scheme_elem:
            return None

        return TaxScheme(
            id=self.unwrap(tax_scheme_elem.get("ID")),
            tax_type_code=self.unwrap(tax_scheme_elem.get("TaxTypeCode")),
        )

    def extract_party_tax_scheme(self, party_tax_scheme_elem, ns=None) -> Optional[PartyTaxScheme]:
        if not party_tax_scheme_elem:
            return None

        # Handle if it's a list (UBL JSON quirk)
        party_tax_scheme_elem = self.unwrap_list(party_tax_scheme_elem)

        # Proper unwrapping of ExemptionReason
        exemption_reason = self.unwrap_and_extract(party_tax_scheme_elem.get("ExemptionReason"))


        return PartyTaxScheme(
            company_id=self.unwrap(party_tax_scheme_elem.get("CompanyID")),
            exemption_reason=exemption_reason,
            tax_scheme=self.extract_tax_scheme(party_tax_scheme_elem.get("TaxScheme", {})),
        )

    def extract_item(self, item_elem, ns=None) -> Optional[Item]:
        if not item_elem:
            return None
        return Item(
            name=self.unwrap_and_extract(item_elem.get("Name")),
            description=self.unwrap_and_extract(item_elem.get("Description")),
            classified_tax_category=None  # Optional: handle if needed later
        )

    def unmarshal_party(self, data: bytes, party_type_elem: str) -> Party:
        """
        Orchestrates party extraction by delegating to extract_* methods.
        """
        order_data = self.load_json(data)

        party_data = order_data.get("Order", {}).get(party_type_elem, {}).get("Party", {})
        if not party_data:
            raise HTTPException(status_code=400, detail=f"Missing {party_type_elem} in JSON")

        party_tax_scheme_raw = party_data.get("PartyTaxScheme", {})
        party_tax_scheme_data = self.unwrap_list(party_tax_scheme_raw)
        registration_name = self.unwrap_and_extract(
                                party_tax_scheme_data.get(
                                    "RegistrationName")) if party_tax_scheme_data else None

        # Handle the case where PartyName is a list
        party_name = self.unwrap(self.unwrap_list(party_data.get("PartyName")).get("Name"))

        return Party(
            endpoint_id=None,  # Set later based on user/session
            party_name=party_name,
            postal_address={
                "street": self.unwrap(party_data.get("PostalAddress", {}).get("StreetName")),
                "city": self.unwrap(party_data.get("PostalAddress", {}).get("CityName")),
                "postal_code": self.unwrap(party_data.get("PostalAddress", {}).get("PostalZone")),
                "country": self.unwrap(party_data.get("PostalAddress", {}).get("CountrySubentity")),
            },
            party_legal_entity={
                "registration_name": registration_name
            },
            contact=self.extract_contact(party_data.get("Contact")),
            party_tax_scheme=self.extract_party_tax_scheme(party_data.get("PartyTaxScheme"))
        )

    def unmarshal_header(self, data: bytes) -> InvoiceHeader:
        """
        Extracts header info and converts it into an InvoiceHeader model.
        """
        order_data = self.load_json(data)

        header_data = order_data.get("Order", {})
        if not header_data:
            raise HTTPException(status_code=400, detail="Missing Order data")

        return InvoiceHeader(
            customization_id=self.unwrap(header_data.get("CustomizationID")),
            profile_id=self.unwrap(header_data.get("ProfileID")),
            invoice_id=None,  # To be set later
            issue_date=self.unwrap(header_data.get("IssueDate")),
            due_date=None,
            invoice_type_code="380",  # Default
            document_currency_code="AUD",  # Default
            buyer_reference=self.unwrap(header_data.get("SalesOrderID")),
            order_reference=self.unwrap(header_data.get("ID")),
        )


    def unmarshal_invoice_lines(self, data: bytes) -> List[InvoiceLine]:
        order_data = self.load_json(data)
        lines_data = order_data.get("Order", {}).get("OrderLine", [])

        invoice_lines = []
        for line in lines_data:
            line_item = line.get("LineItem", {})
            invoice_lines.append(
                InvoiceLine(
                    id=self.unwrap_and_extract(line_item.get("ID")),
                    invoiced_quantity=float(self.unwrap_and_extract(line_item.get("Quantity"))),
                    line_extension_amount=None, #Calculation done later when building
                    item=self.extract_item(line_item.get("Item")),
                    price={
                        "price_amount": float(
                            self.unwrap_and_extract(line_item.get("Price", {}).get("PriceAmount")))
                    }
                )
            )

        return invoice_lines
