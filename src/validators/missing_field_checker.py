#src/validators/missing_field_checker.py

from typing import List
from pydantic import BaseModel
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.domain.models.invoice_response_models import MissingFieldsReport

class MissingFieldChecker:
    def __init__(self, invoice: InvoiceUpdateModel):
        self.invoice = invoice

    MANDATORY_FIELDS = [
        # ---------- Header ----------
        "customization_id",
        "profile_id",
        "id",
        "issue_date",
        "invoice_type_code",
        "document_currency_code",
        "buyer_reference",
        "order_reference.id",
        # ---------- Supplier Party ----------
        "accounting_supplier_party.party_name.name",
        "accounting_supplier_party.postal_address.street_name",
        "accounting_supplier_party.postal_address.city_name",
        "accounting_supplier_party.postal_address.postal_zone",
        "accounting_supplier_party.postal_address.country.identification_code",
        "accounting_supplier_party.party_legal_entity.registration_name",
        "accounting_supplier_party.contact.name",
        "accounting_supplier_party.party_tax_scheme.company_id",
        "accounting_supplier_party.party_tax_scheme.tax_scheme_id",
        # ---------- Customer Party ----------
        "accounting_customer_party.party_name.name",
        "accounting_customer_party.postal_address.street_name",
        "accounting_customer_party.postal_address.city_name",
        "accounting_customer_party.postal_address.postal_zone",
        "accounting_customer_party.postal_address.country.identification_code",
        "accounting_customer_party.party_legal_entity.registration_name",
        "accounting_customer_party.contact.name",
        "accounting_customer_party.party_tax_scheme.company_id",
        "accounting_customer_party.party_tax_scheme.tax_scheme_id",
        # ---------- Invoice Totals ----------
        "legal_monetary_total.payable_amount",
        "legal_monetary_total.line_extension_amount",
    ]

    MANDATORY_FIELDS_PER_LINE = [
        "id",
        "invoiced_quantity",
        "unit_code",
        "line_extension_amount",
        "item.name",
        "item.classified_tax_category.id",
        "item.classified_tax_category.percent",
        "item.classified_tax_category.tax_scheme_id",
        "price.price_amount",
    ]

    def run(self) -> MissingFieldsReport:
        """
        Runs the missing field check and returns a structured report.
        """
        header_missing = self._find_missing_fields()
        line_missing = self._find_missing_fields_per_line()
        return MissingFieldsReport(
            missing_invoice_fields=header_missing,
            missing_invoice_lines=line_missing
        )

    def _find_missing_fields(self) -> List[str]:
        missing = []
        for field_path in self.MANDATORY_FIELDS:
            if not self._resolve_field(self.invoice, field_path):
                missing.append(field_path)
        return missing

    def _find_missing_fields_per_line(self) -> List[str]:
        missing = []
        if self.invoice.invoice_lines:
            for idx, line in enumerate(self.invoice.invoice_lines):
                for field_path in self.MANDATORY_FIELDS_PER_LINE:
                    if not self._resolve_field(line, field_path):
                        missing.append(f"invoice_lines[{idx}].{field_path}")
        else:
            missing.append("invoice_lines: No lines present")
        return missing

    def _resolve_field(self, instance: BaseModel, field_path: str):
        current = instance
        for part in field_path.split("."):
            if isinstance(current, BaseModel):
                current = getattr(current, part, None)
            elif isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
