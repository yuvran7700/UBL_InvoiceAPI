from typing import List, Optional
from pydantic import BaseModel
from datetime import date

# Reuse existing nested models but make nested fields optional for PATCH

class Country(BaseModel):
    identification_code: Optional[str]  # REQUIRED in Party PostalAddress

class Address(BaseModel): #REQUIRED
    street_name: Optional[str]
    additional_street_name: Optional[str]
    city_name: Optional[str]
    postal_zone: Optional[str]
    country_subentity: Optional[str]
    address_line: Optional[str]
    country: Optional[Country]  # REQUIRED

class PartyIdentification(BaseModel):
    id: Optional[str]  # REQUIRED

class PartyName(BaseModel):
    name: Optional[str]  # REQUIRED

class PartyTaxScheme(BaseModel):
    company_id: Optional[str]
    tax_scheme_id: Optional[str] #REQUIRED - GST registration

class PartyLegalEntity(BaseModel):
    registration_name: Optional[str]
    company_id: Optional[str]
    company_legal_form: Optional[str]

class Contact(BaseModel):
    name: Optional[str]
    telephone: Optional[str]
    electronic_mail: Optional[str]

class Party(BaseModel):
    party_identification: Optional[PartyIdentification]  # REQUIRED - ABN or similar
    party_name: Optional[PartyName]  # REQUIRED
    postal_address: Optional[Address]  # REQUIRED
    party_tax_scheme: Optional[PartyTaxScheme]
    party_legal_entity: Optional[PartyLegalEntity]
    contact: Optional[Contact]

class InvoicePeriod(BaseModel):
    start_date: Optional[date]
    end_date: Optional[date]

class OrderReference(BaseModel):
    id: Optional[str]
    sales_order_id: Optional[str]

class DocumentReference(BaseModel):
    id: Optional[str]
    document_type_code: Optional[str]

class TaxCategory(BaseModel):
    id: Optional[str]
    percent: Optional[float]
    tax_scheme_id: Optional[str]

class AllowanceCharge(BaseModel):
    charge_indicator: Optional[bool]
    allowance_charge_reason_code: Optional[str]
    allowance_charge_reason: Optional[str]
    multiplier_factor_numeric: Optional[float]
    amount: Optional[float]
    base_amount: Optional[float]
    tax_category: Optional[TaxCategory]

class TaxSubtotal(BaseModel):
    taxable_amount: Optional[float]
    tax_amount: Optional[float]
    tax_category: Optional[TaxCategory]

class TaxTotal(BaseModel):
    tax_amount: Optional[float]
    tax_subtotals: Optional[List[TaxSubtotal]]

class MonetaryTotal(BaseModel):
    line_extension_amount: Optional[float] # REQUIRED
    tax_exclusive_amount: Optional[float] # REQUIRED
    tax_inclusive_amount: Optional[float] # REQUIRED
    charge_total_amount: Optional[float]
    prepaid_amount: Optional[float]
    payable_amount: Optional[float]  # REQUIRED

class ItemClassification(BaseModel):
    item_classification_code: Optional[str]

class ClassifiedTaxCategory(BaseModel):
    id: Optional[str]
    percent: Optional[float]
    tax_scheme_id: Optional[str]

class Item(BaseModel):
    description: Optional[str]  # REQUIRED (PEPPOL/AUNZ)
    name: Optional[str]
    buyers_item_id: Optional[str]
    sellers_item_id: Optional[str]
    standard_item_id: Optional[str]
    origin_country: Optional[Country]
    commodity_classification: Optional[ItemClassification]
    classified_tax_category: Optional[ClassifiedTaxCategory]

class Price(BaseModel):
    price_amount: Optional[float]  # REQUIRED
    allowance_charge_amount: Optional[float]
    base_amount: Optional[float]

class InvoiceLine(BaseModel):
    id: Optional[str]  # REQUIRED
    note: Optional[str]
    invoiced_quantity: Optional[float]  # REQUIRED
    unit_code: Optional[str]  # REQUIRED
    line_extension_amount: Optional[float]  # REQUIRED
    accounting_cost: Optional[str]
    invoice_period: Optional[InvoicePeriod]
    order_line_reference: Optional[str]
    document_reference: Optional[DocumentReference]
    item: Optional[Item]  # REQUIRED
    price: Optional[Price]  # REQUIRED

class InvoiceUpdateModel(BaseModel):
    customization_id: Optional[str]  # REQUIRED
    profile_id: Optional[str]  # REQUIRED
    id: Optional[str]  # REQUIRED (Invoice Number)
    issue_date: Optional[date]  # REQUIRED
    invoice_type_code: Optional[str]  # REQUIRED (e.g., '380' = Tax Invoice)
    document_currency_code: Optional[str]  # REQUIRED (e.g., AUD)

    due_date: Optional[date]
    note: Optional[str]
    accounting_cost: Optional[str]
    buyer_reference: Optional[str]

    invoice_period: Optional[InvoicePeriod]
    order_reference: Optional[OrderReference]

    accounting_supplier_party: Optional[Party]  # REQUIRED
    accounting_customer_party: Optional[Party]  # REQUIRED
    payee_party: Optional[Party]
    tax_representative_party: Optional[Party]

    delivery_date: Optional[date]
    delivery_address: Optional[Address]
    payment_means_code: Optional[str]
    payment_id: Optional[str]
    payee_financial_account_id: Optional[str]
    payment_terms_note: Optional[str]

    allowance_charges: Optional[List[AllowanceCharge]]
    tax_total: Optional[TaxTotal]
    legal_monetary_total: Optional[MonetaryTotal]  # REQUIRED
    invoice_lines: Optional[List[InvoiceLine]]  # REQUIRED (At least one line)