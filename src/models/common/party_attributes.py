from typing import Optional
from pydantic import BaseModel
from .contact import Contact
from .tax_scheme import PartyTaxScheme


class PartyAttributes(BaseModel):
    """
    Unified Pydantic model representing a party (buyer or seller).
    """

    customer_assigned_account_id: str
    supplier_assigned_account_id: str
    party_name: str
    address: str
    endpoint_id: Optional[str] = None
    # Nested models
    contact: Optional[Contact] = None
    tax_scheme: Optional[PartyTaxScheme] = None
