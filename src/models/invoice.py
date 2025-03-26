from typing import List, Optional, Dict
from pydantic import BaseModel
from datetime import date

from src.models.tax import ClassifiedTaxCategoryPatch, TaxScheme

class InvoiceHeader(BaseModel):
    customization_id: str
    profile_id: str
    invoice_id: Optional[str]
    issue_date: date
    due_date: Optional[date]
    invoice_type_code: str
    document_currency_code: str
    buyer_reference: Optional[str] #Order Document's order number
    order_reference: Optional[str] #Order Document's unique identifier


class PartyTaxScheme(BaseModel):
    company_id: str
    exemption_reason: Optional[str] = None
    tax_scheme: TaxScheme

class Contact(BaseModel):
    name: str
    telephone: Optional[str] = None
    telefax: Optional[str] = None
    electronic_mail: Optional[str] = None

class Party(BaseModel):
    endpoint_id: Optional[str] #to be set later
    party_name: str 
    postal_address: Dict[str, str]  # Address of the party (e.g., street, city, postal code)
    party_legal_entity: Dict[str, str]  # RegistrattionName - found in <cac:PartyTaxScheme>/<cbc:RegistrationName>

    # Using the nested models for more detailed information
    contact: Optional[Contact] = None  # Optional contact information for the party
    party_tax_scheme: Optional[PartyTaxScheme] = None  # Optional tax scheme for the party



class Item(BaseModel):
    name: str
    description: Optional[str]
    classified_tax_category: Optional["ClassifiedTaxCategoryPatch"]  #Nested object - To be added by user later
    
class Price(BaseModel):
    price_amount: float

class InvoiceLine(BaseModel):
    id: str
    invoiced_quantity: float
    line_extension_amount: Optional[float]
    item: Item
    price: Price


class LegalMonetaryTotal(BaseModel):
    line_extension_amount: float = 0.0
    tax_exclusive_amount: Optional[float] = None
    tax_inclusive_amount: Optional[float] = None
    payable_amount: Optional[float] = None

class Invoice(BaseModel):
    header: InvoiceHeader
    accounting_supplier_party: Party
    accounting_customer_party: Party
    invoice_lines: List[InvoiceLine]
    legal_monetary_total: LegalMonetaryTotal
