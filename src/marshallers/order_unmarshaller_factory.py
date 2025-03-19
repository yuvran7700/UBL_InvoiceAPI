
from abc import ABC, abstractmethod
from typing import Dict, Optional

class OrderUnmarshaller(ABC):
    """
    Interface for unmarshalling order data from various formats (XML, JSON).
    """

    @abstractmethod
    def unmarshal_header(self, content: str) -> dict:
        """
        Abstract method to unmarshal the header fields from the order content.
        """
        pass

    @abstractmethod
    def unmarshal_party(self, content: str) -> 'Party':
        """
        Abstract method to unmarshal a Party object from the order content.
        """
        pass
    
