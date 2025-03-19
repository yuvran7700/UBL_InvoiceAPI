import json
from fastapi import HTTPException
from typing import Optional

from src.models.invoice import Contact, InvoiceHeader, Party, PartyTaxScheme
from src.models.tax import TaxScheme
from src.marshallers.order_unmarshaller_factory import OrderUnmarshaller

class OrderJsonUnmarshaller(OrderUnmarshaller):
    """
    Utility class to unmarshal structured order data from JSON format.
    """

    def unmarshal_header(self, json_content: bytes) -> InvoiceHeader:
        try:
            order_data = json.loads(json_content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")

        header = InvoiceHeader(
            customization_id=order_data.get("Order", {}).get("CustomizationID", {}).get("_"),
            profile_id=order_data.get("Order", {}).get("ProfileID", {}).get("_"),
            invoice_id=None,  # Set later by the user
            issue_date=order_data.get("Order", {}).get("IssueDate", {}).get("_"),
            due_date=None,  # Set later by the user
            invoice_type_code="380",  # Default
            document_currency_code="AUD",  # Default
            buyer_reference=order_data.get("Order", {}).get("SalesOrderID", {}).get("_"),
            order_reference=order_data.get("Order", {}).get("ID", {}).get("_")
        )
        return header

    def unmarshal_contact(contact_data) -> Optional[Contact]:
        """
        Helper function to unmarshal contact details from JSON data.
        """
        if not contact_data:
            return None

        return Contact(
            name=contact_data.get("Name", {}).get("_"),
            telephone=contact_data.get("Telephone", {}).get("_"),
            telefax=contact_data.get("Telefax", {}).get("_"),
            electronic_mail=contact_data.get("ElectronicMail", {}).get("_")
        )
    
    def unmarshal_party_tax_scheme(party_tax_scheme_data) -> Optional[PartyTaxScheme]:
        """
        Helper function to unmarshal party tax scheme from JSON data.
        """
        if not party_tax_scheme_data:
            return None
        
        tax_scheme_data = party_tax_scheme_data.get("TaxScheme", {})
        
        return PartyTaxScheme(
            registration_name=party_tax_scheme_data.get("RegistrationName", {}).get("_"),
            company_id=party_tax_scheme_data.get("CompanyID", {}).get("_"),
            exemption_reason=party_tax_scheme_data.get("ExemptionReason", [{}])[0].get("_"),
            tax_scheme=TaxScheme(
                id=tax_scheme_data.get("ID", {}).get("_"),
                tax_type_code=tax_scheme_data.get("TaxTypeCode", {}).get("_")
            ) if tax_scheme_data else None
        )

    def unmarshal_party(json_content: str) -> Party:
        """
        Unmarshals a Party object from the provided JSON content.
        """
        try:
            order_data = json.loads(json_content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")
        
        party_data = order_data.get("Party", {})
        
        # Extract basic party info
        party_name = party_data.get("PartyName", {}).get("Name", {}).get("_")
        postal_address = {
            "street": party_data.get("PostalAddress", {}).get("StreetName", {}).get("_"),
            "city": party_data.get("PostalAddress", {}).get("CityName", {}).get("_"),
            "postal_code": party_data.get("PostalAddress", {}).get("PostalZone", {}).get("_"),
            "country": party_data.get("PostalAddress", {}).get("Country", {}).get("IdentificationCode", {}).get("_")
        }
        party_legal_entity = {"registration_name": party_data.get("PartyLegalEntity", {}).get("RegistrationName", {}).get("_")}

        # Extract Contact info (if exists)
        contact_data = party_data.get("Contact", {})
        contact = OrderJsonUnmarshaller.unmarshal_contact(contact_data)
        
        # Extract PartyTaxScheme info (if exists)
        party_tax_scheme_data = party_data.get("PartyTaxScheme", {})
        party_tax_scheme = OrderJsonUnmarshaller.unmarshal_party_tax_scheme(party_tax_scheme_data)

        return Party(
            endpoint_id=None,  # Set by the user later (e.g., JWT token)
            party_identification=[],  # Set later if needed (e.g., VAT IDs)
            party_name=party_name,
            postal_address=postal_address,
            party_legal_entity=party_legal_entity,
            contact=contact,
            party_tax_scheme=party_tax_scheme
        )
