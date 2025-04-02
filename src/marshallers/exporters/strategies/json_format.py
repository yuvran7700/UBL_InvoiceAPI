import json
from src.models.invoice_update import InvoiceUpdateModel
from src.marshallers.exporters.strategies.invoice_export_strategy import InvoiceExportStrategy

class JsonInvoiceFormatter(InvoiceExportStrategy):
    def serialize(self, invoice: InvoiceUpdateModel) -> bytes:
        return json.dumps(
            invoice.dict(by_alias=True, exclude_none=True), 
            indent=2, 
            default=str
            ).encode("utf-8")
