from abc import ABC, abstractmethod
from src.domain.models.invoice_update import InvoiceUpdateModel

class InvoiceExportStrategy(ABC):
    @abstractmethod
    def serialize(self, invoice: InvoiceUpdateModel) -> bytes:
        ...
