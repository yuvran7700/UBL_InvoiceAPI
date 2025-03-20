from typing import Optional
import xml.etree.ElementTree as ET
from datetime import datetime
from fastapi import HTTPException
from src.models.invoice import InvoiceHeader, Party, PartyTaxScheme, Contact
from src.models.tax import TaxScheme
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller

class OrderXmlUnmarshaller(OrderUnmarshaller):
    """
    Concrete implementation of the abstract factory to unmarshall order data from XML.
    """

    NAMESPACES = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    def get_text(self, element, path, required=False, ns=None):
        """
        Retrieves the trimmed text from an XML element based on the provided XPath.
        """
        ns = ns or OrderXmlUnmarshaller.NAMESPACES
        child = element.find(path, ns)
        text = (
            child.text.strip() if child is not None and child.text is not None else None
        )
        if required and not text:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required element: {path}",
            )
        return text

    def parse_date(self, text, field_name):
        """
        Parses a date string in the format YYYY-MM-DD.
        """
        try:
            return datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid {field_name} format")

    def extract_contact(self, contact_elem, ns=None) -> Optional[Contact]:
        """
        Extracts a Contact object from an XML element.
        """
        if contact_elem is None:
            return None
        ns = ns or OrderXmlUnmarshaller.NAMESPACES
        return Contact(
            name=self.get_text(contact_elem, ".//cbc:Name", required=True, ns=ns),
            telephone=self.get_text(contact_elem, ".//cbc:Telephone", ns=ns),
            telefax=self.get_text(contact_elem, ".//cbc:Telefax", ns=ns),
            electronic_mail=self.get_text(contact_elem, ".//cbc:ElectronicMail", ns=ns),
        )

    def extract_tax_scheme(self, tax_scheme_elem, ns=None) -> TaxScheme:
        """
        Extracts a TaxScheme object from an XML element.
        """
        if tax_scheme_elem is None:
            return None
        ns = ns or OrderXmlUnmarshaller.NAMESPACES
        return TaxScheme(
            id=self.get_text(tax_scheme_elem, "./cbc:ID", required=True, ns=ns),
            tax_type_code=self.get_text(tax_scheme_elem, "./cbc:TaxTypeCode", ns=ns),
        )

    def extract_party_tax_scheme(self, party_tax_scheme_elem, ns=None) -> PartyTaxScheme:
        """
        Extracts a PartyTaxScheme object from an XML element.
        """
        if party_tax_scheme_elem is None:
            return None
        ns = ns or OrderXmlUnmarshaller.NAMESPACES
        tax_scheme_elem = party_tax_scheme_elem.find("./cac:TaxScheme", ns)
        return PartyTaxScheme(
            company_id=self.get_text(
                party_tax_scheme_elem, "./cbc:CompanyID", required=True, ns=ns
            ),
            exemption_reason=self.get_text(
                party_tax_scheme_elem, "./cbc:ExemptionReason", ns=ns
            ),
            tax_scheme=self.extract_tax_scheme(tax_scheme_elem, ns),
        )

    def unmarshal_party(self, data: bytes, party_type_elem: str) -> Party:
        """
        Extracts a Party object based on the provided XML content and the party type element (e.g., Buyer or Seller).
        """
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        ns = OrderXmlUnmarshaller.NAMESPACES

        # Get the party element (either BuyerCustomerParty or SellerSupplierParty)
        party_elem = root.find(f".//{party_type_elem}", ns)
        if party_elem is None:
            raise HTTPException(status_code=400, detail=f"Missing {party_type_elem} in XML")

        # Extract party details
        party_name = self.get_text(party_elem, ".//cac:PartyName/cbc:Name", required=True, ns=ns)
        postal_address_elem = party_elem.find(".//cac:PostalAddress", ns)
        contact_elem = party_elem.find(".//cac:Contact", ns)
        party_tax_scheme_elem = party_elem.find(".//cac:PartyTaxScheme", ns)

        postal_address = {
            "street": self.get_text(postal_address_elem, "./cbc:StreetName", ns=ns),
            "city": self.get_text(postal_address_elem, "./cbc:CityName", ns=ns),
            "postal_code": self.get_text(postal_address_elem, "./cbc:PostalZone", ns=ns),
            "country": self.get_text(postal_address_elem, "./cbc:CountrySubentity", ns=ns),
        }

        # Extract party legal entity (registration name)
        party_legal_entity = {
            "registration_name": self.get_text(party_elem, ".//cac:PartyTaxScheme/cbc:RegistrationName", ns=ns)
        }

        contact = self.extract_contact(contact_elem, ns)
        party_tax_scheme = self.extract_party_tax_scheme(party_tax_scheme_elem, ns)

        return Party(
            endpoint_id=None,  # Set by the user later (e.g., JWT token)
            party_name=party_name,
            postal_address=postal_address,
            party_legal_entity=party_legal_entity,  # Placeholder for now, can be extended
            contact=contact,
            party_tax_scheme=party_tax_scheme,
        )

    def unmarshal_header(self, data: bytes) -> InvoiceHeader:
        """
        Extracts the header fields from the provided UBL XML content and returns an InvoiceHeader object.
        """
        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        ns = OrderXmlUnmarshaller.NAMESPACES

        header = InvoiceHeader(
            customization_id=self.get_text(root, "./cbc:CustomizationID", ns=ns),
            profile_id=self.get_text(root, "./cbc:ProfileID", ns=ns),
            invoice_id=None,  # Set later by the user
            issue_date=self.parse_date(self.get_text(root, "./cbc:IssueDate", ns=ns), "IssueDate"),
            due_date=None,  # Set later by the user
            invoice_type_code="380",  # Default
            document_currency_code="AUD",  # Default
            buyer_reference=self.get_text(root, "./cbc:SalesOrderID", ns=ns),
            order_reference=self.get_text(root, "./cbc:ID", ns=ns),
        )
        return header