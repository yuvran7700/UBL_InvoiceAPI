from pydantic import BaseModel
from typing import Optional


class ClassifiedTaxCategoryPatch(BaseModel):
    cbc_id: Optional[str]  # VAT category code
    cbc_percent: Optional[float]  # VAT rate
    tax_scheme_id: Optional[str]  # Tax scheme ID


class TaxScheme(BaseModel):
    id: str
    tax_type_code: Optional[str]
