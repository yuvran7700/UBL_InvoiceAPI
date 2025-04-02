from fastapi import HTTPException
from src.marshallers.exporters.strategies.invoice_export_strategy import InvoiceExportStrategy
from src.marshallers.exporters.strategies.json_format import JsonInvoiceFormatter
from src.marshallers.exporters.strategies.xml_format import XmlInvoiceFormatter
from src.models.invoice_update import InvoiceUpdateModel


class FormatterFactory:

    def create(self, format: str) -> InvoiceExportStrategy:
        if format == "json":
            return JsonInvoiceFormatter()
        elif format == "xml":
            return XmlInvoiceFormatter()
        else:
            raise HTTPException(status_code=415, detail="Unsupported format.")

    def serialize(self, invoice: InvoiceUpdateModel, format: str) -> bytes:
        return self.create(format).serialize(invoice)
