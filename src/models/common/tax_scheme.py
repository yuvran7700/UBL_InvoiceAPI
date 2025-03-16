from typing import Optional
from pydantic import BaseModel

class TaxScheme(BaseModel):
    """
    Model representing a tax scheme.
    """
    id: str  # For example, "UK VAT"
    tax_type_code: Optional[str] = None  # e.g., "VAT"

class PartyTaxScheme(BaseModel):
    """
    Model representing tax scheme details for a party.
    """
    registration_name: Optional[str] = None
    company_id: str
    exemption_reason: Optional[str] = None
    tax_scheme: TaxScheme
