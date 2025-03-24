
""""
Defines the abstract strategy interface for parsing UBL order data 
    from different formats (XML, JSON).
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.invoice import Contact, InvoiceLine, Item, Party, PartyTaxScheme
from src.models.tax import TaxScheme

class OrderParsingStrategy(ABC):
    """
    Abstract strategy interface defining the contract for parsing UBL order data
    from different formats (XML, JSON).
    """

    @abstractmethod
    def extract_contact(self, contact_elem, ns=None) -> Optional[Contact]:
        """
        Extracts contact details from the provided element.

        Args:
            contact_elem (any): The element containing contact information.
            ns (any, optional): Namespace information, if applicable.

        Returns:
            Optional[Contact]: A `Contact` object if data is available, otherwise `None`.
        """
        pass

    @abstractmethod
    def extract_tax_scheme(self, tax_scheme_elem, ns=None) -> Optional[TaxScheme]:
        """
        Extracts tax scheme details from the provided element.

        Args:
            tax_scheme_elem (any): The element containing tax scheme information.
            ns (any, optional): Namespace information, if applicable.

        Returns:
            Optional[TaxScheme]: A `TaxScheme` object if data is available, otherwise `None`.
        """
        pass

    @abstractmethod
    def extract_party_tax_scheme(self, party_tax_scheme_elem, ns=None) -> Optional[PartyTaxScheme]:
        """
        Extracts party tax scheme details from the provided element.

        Args:
            party_tax_scheme_elem (any): The element containing party tax scheme information.
            ns (any, optional): Namespace information, if applicable.

        Returns: Optional[PartyTaxScheme]: 
            A `PartyTaxScheme` object if data is available, otherwise `None`.
        """
        pass

    @abstractmethod
    def extract_item(self, item_elem, ns=None) -> Optional[Item]:
        """
        Parse individual order line items and item model.
        """
        pass

    @abstractmethod
    def unmarshal_party(self, data: bytes, party_type_elem: str) -> Party:
        """
        Parse buyer or supplier party section based on party_type.
        """
        pass

    @abstractmethod
    def unmarshal_header(self, data: bytes) -> dict:
        """
        Parse the order header section and return an InvoiceHeader model.
        """
        pass

    @abstractmethod
    def unmarshal_invoice_lines(self, data: bytes) -> List[InvoiceLine]:
        """
        Parse all order line items and return a list of InvoiceLine models.
        """
        pass
