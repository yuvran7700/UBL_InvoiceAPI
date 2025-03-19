
from abc import ABC, abstractmethod
from typing import Dict, Optional

from src.models.invoice import Contact, Party, PartyTaxScheme
from src.models.tax import TaxScheme

class OrderUnmarshaller(ABC):
    """
    Interface for unmarshalling order data from various formats (XML, JSON).
    """

    @abstractmethod
    def get_text(self, element, path, required=False, error_message=None, ns=None) -> str:
        pass
    
    @abstractmethod
    def extract_contact(self, contact_elem, ns=None) -> Optional[Contact]:
        pass

    @abstractmethod
    def extract_tax_scheme(self, tax_scheme_elem, ns=None) -> Optional[TaxScheme]:
        pass

    @abstractmethod
    def extract_party_tax_scheme(self, party_tax_scheme_elem, ns=None) -> Optional[PartyTaxScheme]:
        pass
    
    @abstractmethod
    def unmarshal_party(self, data: bytes, party_type_elem: str) -> Party:
        pass
    
    @abstractmethod
    def unmarshal_header(self, data: bytes) -> dict:
        pass

    
    
    
    
    
