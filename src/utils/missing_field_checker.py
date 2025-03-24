from src.models.invoice import Invoice
from typing import List
from operator import attrgetter

MANDATORY_FIELDS = [
    "header.invoice_id",
    "header.due_date",
    "supplier_party.party_name",
    "supplier_party.postal_address.street",
    "customer_party.party_name",
    "total.payable_amount"
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
