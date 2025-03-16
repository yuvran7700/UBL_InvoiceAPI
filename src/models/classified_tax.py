# src/models/classified_tax.py
from pydantic import BaseModel


class TaxScheme(BaseModel):
    ID: str


class ClassifiedTaxCategory(BaseModel):
    ID: str  # Tax category code, e.g., "S"
    Percent: float  # Tax rate (e.g., 10 or 15)
    TaxScheme: TaxScheme
