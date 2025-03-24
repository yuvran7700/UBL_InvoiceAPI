
from typing import List
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
    "supplier_party.party_name",
    "supplier_party.postal_address.street",
    "supplier_party.postal_address.city",
    "supplier_party.postal_address.postal_code",
    "supplier_party.postal_address.country",
    "supplier_party.party_legal_entity.registration_name",
    "supplier_party.contact.name",
    "supplier_party.party_tax_scheme.company_id",
    "supplier_party.party_tax_scheme.tax_scheme.id",

    # ---------- Customer Party ----------
    "customer_party.party_name",
    "customer_party.postal_address.street",
    "customer_party.postal_address.city",
    "customer_party.postal_address.postal_code",
    "customer_party.postal_address.country",
    "customer_party.party_legal_entity.registration_name",
    "customer_party.contact.name",
    "customer_party.party_tax_scheme.company_id",
    "customer_party.party_tax_scheme.tax_scheme.id",

    # ---------- Invoice Totals ----------
    "total.payable_amount",

    # ---------- Invoice Lines Mandatory Fields (checking first line) ----------
    "invoice_lines",
    "invoice_lines[0].id",
    "invoice_lines[0].invoiced_quantity",
    "invoice_lines[0].line_extension_amount",
    "invoice_lines[0].item.name",

    # ---------- Nested Classified Tax Category ----------
    "invoice_lines[0].item.classified_tax_category.cbc_id",
    "invoice_lines[0].item.classified_tax_category.cbc_percent",
    "invoice_lines[0].item.classified_tax_category.tax_scheme_id",

    # ---------- Pricing ----------
    "invoice_lines[0].price.price_amount"
]


def find_missing_fields(invoice: Invoice) -> List[str]:
    missing = []
    for field_path in MANDATORY_FIELDS:
        try:
            # Dynamically walk through nested attributes/dict keys
            parts = field_path.split('.')
            current = invoice
            for part in parts:
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    current = getattr(current, part, None)
            if current is None:
                missing.append(field_path)
        except AttributeError:
            missing.append(field_path)
    return missing
