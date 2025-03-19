import xml.etree.ElementTree as ET
from fastapi import HTTPException
from src.models.invoice import InvoiceHeader, Party
from src.models.tax import TaxScheme
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller

class OrderXmlUnmarshaller(OrderUnmarshaller):
    NAMESPACES = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    }

    def get_text(self, element, path, required=False, ns=None):
        ns = ns or self.NAMESPACES
        child = element.find(path, ns)
        text = child.text.strip() if child is not None and child.text is not None else None
        if required and not text:
            raise HTTPException(status_code=400, detail=f"Missing required element: {path}")
        return text

    def unmarshal_header(self, xml_content: bytes) -> InvoiceHeader:
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        
        header = InvoiceHeader(
            customization_id=self.get_text(root, "./cbc:CustomizationID"),
            profile_id=self.get_text(root, "./cbc:ProfileID"),
            invoice_id=None,  # Set later by the user
            issue_date=self.get_text(root, "./cbc:IssueDate"),
            due_date=None,  # Set later by the user
            invoice_type_code="380",  # Default
            document_currency_code="AUD",  # Default
            buyer_reference=self.get_text(root, "./cbc:SalesOrderID"),
            order_reference=self.get_text(root, "./cbc:ID")
        )
        return header

    def unmarshal_party(self, xml_content: bytes) -> Party:
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")
        
        party_elem = root.find(".//cac:BuyerCustomerParty/cac:Party", self.NAMESPACES)
        if party_elem is None:
            raise HTTPException(status_code=400, detail="Missing party information in XML")

        # Extract party details
        party_name = self.get_text(party_elem, ".//cbc:Name")
        postal_address = {
            "street": self.get_text(party_elem, ".//cac:PostalAddress/cbc:StreetName"),
            "city": self.get_text(party_elem, ".//cac:PostalAddress/cbc:CityName"),
            "postal_code": self.get_text(party_elem, ".//cac:PostalAddress/cbc:PostalZone"),
            "country": self.get_text(party_elem, ".//cac:PostalAddress/cbc:Country/cbc:IdentificationCode")
        }

        # Return Party object
        return Party(
            endpoint_id=None,  # Set later
            party_identification=[],
            party_name=party_name,
            postal_address=postal_address,
            party_legal_entity={},  # Placeholder, could be extracted if needed
            #nested models
            contact=None,  # Set if available
            party_tax_scheme=None  # Set if available
        )
