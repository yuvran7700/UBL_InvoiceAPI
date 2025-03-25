#src/utils/missing_field_checker.py

from typing import List
from pydantic import BaseModel
from src.models.invoice import Invoice

MANDATORY_FIELDS = [
    # ---------- Header ----------
    "header.customization_id",
    "header.profile_id",
    "header.invoice_id",
    "header.issue_date",
    "header.due_date",
    "header.invoice_type_code",
    "header.document_currency_code",
    "header.buyer_reference",
    "header.order_reference",

    # ---------- Supplier Party ----------
    "accounting_supplier_party.party_name",
    "accounting_supplier_party.postal_address.street",
    "accounting_supplier_party.postal_address.city",
    "accounting_supplier_party.postal_address.postal_code",
    "accounting_supplier_party.postal_address.country",
    "accounting_supplier_party.party_legal_entity.registration_name",
    "accounting_supplier_party.contact.name",
    "accounting_supplier_party.party_tax_scheme.company_id",
    "accounting_supplier_party.party_tax_scheme.tax_scheme.id",

    # ---------- Customer Party ----------
    "accounting_customer_party.party_name",
    "accounting_customer_party.postal_address.street",
    "accounting_customer_party.postal_address.city",
    "accounting_customer_party.postal_address.postal_code",
    "accounting_customer_party.postal_address.country",
    "accounting_customer_party.party_legal_entity.registration_name",
    "accounting_customer_party.contact.name",
    "accounting_customer_party.party_tax_scheme.company_id",
    "accounting_customer_party.party_tax_scheme.tax_scheme.id",

    # ---------- Invoice Totals ----------
    "legal_monetary_total.payable_amount",
    "legal_monetary_total.line_extension_amount",
    
]

MANDATORY_FIELDS_PER_LINE = [
    "id",
    "invoiced_quantity",
    "line_extension_amount",
    "item.name",
    "item.classified_tax_category.cbc_id",
    "item.classified_tax_category.cbc_percent",
    "item.classified_tax_category.tax_scheme_id",
    "price.price_amount",
]


def find_missing_fields(invoice: Invoice) -> List[str]:
    data = invoice
    missing = []

    for field_path in MANDATORY_FIELDS:
        parts = field_path.split('.')
        current = data
        for part in parts:
            if isinstance(current, BaseModel):
                current = getattr(current, part, None)
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                current = None
                break
        if current is None:
            missing.append(field_path)
    return missing


def drill_down(current, field_path):
    for part in field_path.split('.'):
        if isinstance(current, BaseModel):
            current = getattr(current, part, None)
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current
