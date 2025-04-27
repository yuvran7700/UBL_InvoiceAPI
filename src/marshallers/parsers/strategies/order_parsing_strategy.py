""" "
Defines the abstract strategy interface for parsing UBL order data
    from different formats (XML, JSON).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union

from src.domain.models.invoice_update import (
    Address, Contact, InvoiceLine, Item, Party, PartyLegalEntity, PartyTaxScheme,
    InvoicePeriod, OrderReference
)
class OrderParsingStrategy(ABC):
    """
    Abstract strategy interface defining the contract for parsing UBL order data
    from different formats (XML, JSON).
    """

    @abstractmethod
    def load_data(self, data: Union[bytes, str]) -> Any:
        """
        Loads the raw data (JSON/XML) and returns a parsed object
        (e.g., dict for JSON or ElementTree for XML).
        """
        pass

    @abstractmethod
    def extract_person(self, person_elum: Any) -> Optional[str]:
        """
        Extracts person details from the provided element.

        Args:
            persona_elem (any): The element containing person] information.
            ns (any, optional): Namespace information, if applicable.

        Returns:
            Optional[Contact]: A `Contact` object if data is available, otherwise `None`.
        """
        pass

    @abstractmethod
    def extract_contact(self, contact_elem: Any, party_elem: Any) -> Optional[Contact]:
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
    def extract_party_legal_entity(self, party_legal_entity_elemL: Any) -> Optional[PartyLegalEntity]:
        """
        Extracts party legal entity details from the provided element.

        Args:
            party_legal_entity_elem (any): The element containing party tax scheme information.
            ns (any, optional): Namespace information, if applicable.

        Returns: Optional[PartyTaxScheme]:
            A `PartyLegalEntity` object if data is available, otherwise `None`.
        """
        pass

    @abstractmethod
    def extract_party_tax_scheme(self, party_tax_scheme_elem: Any) -> Optional[PartyTaxScheme]:
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
    def extract_address(self, address_elem: Any) -> Optional[Address]:
        """
        Extracts address details from the provided element.
        """
        pass

    @abstractmethod
    def extract_item(self, item_elem: Any) -> Optional[Item]:
        """
        Parse individual order line items and item model.
        """
        pass

    @abstractmethod
    def extract_party(self, order_data: Any, party_type_elem: str) -> Optional[Party]:
        """
        Parse buyer or supplier party section based on party_type.
        """
        pass

    @abstractmethod
    def extract_invoice_period(self, period_elem: Any) -> Optional[InvoicePeriod]:
        """
        Extracts invoice period details from the provided element.
        """
        pass

    @abstractmethod
    def extract_order_reference(self, ref_elem: Any) -> Optional[OrderReference]:
        """
        Extracts order reference details from the provided element.
        """
        pass

    @abstractmethod
    def extract_invoice_lines(self, lines_data: Any) -> List[InvoiceLine]:
        """
        Parse all order line items and return a list of InvoiceLine models.
        """
        pass

    @abstractmethod
    def extract_header_fields(self, order_data: Any) -> Dict[str, Optional[Union[str, float]]]:
        """
        Extracts top-level order metadata fields needed for invoice assembly.
        """
        pass

    @abstractmethod
    def get_order_lines(self, order_data: Any) -> List[Any]:
        """
        Uniform way to fetch the order lines section for both JSON and XML.
        """
        pass
