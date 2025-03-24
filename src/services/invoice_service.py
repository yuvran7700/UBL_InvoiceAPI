"""
Invoice service module.
Handles the creation and persistence of invoices from orders.
"""

from fastapi import HTTPException
from typing import Dict
from src.marshallers.strategies.xml_order_parser import XmlOrderParser
from src.marshallers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.invoice_marshaller import InvoiceMarshaller
from src.validators.invoice_validator import InvoiceValidator
from src.models.invoice import Invoice

class InvoiceService:
    """
    Service layer responsible for orchestrating invoice generation
    from UBL order data.
    """

    def generate_draft_invoice(self, content: bytes, file_type: str) -> dict:
        """
        Generates a draft Invoice from the uploaded UBL order data.

        :param content: Raw bytes of the uploaded order file.
        :param file_type: MIME type of the uploaded file (determined by the route).
        :return: Dictionary containing the Invoice and any missing mandatory fields.
        """
        # Select the correct parsing strategy
        parser = self._select_parsing_strategy(file_type)

        # Assemble the Invoice using the marshaller
        assembler = InvoiceMarshaller(parser)
        invoice: Invoice = assembler.marshal(content)

        # Validate required fields
        missing_fields = InvoiceValidator.validate(invoice)

        return {
            "invoice": invoice,
            "missing_fields": missing_fields
        }

    def _select_parsing_strategy(self, file_type: str):
        """
        Determines the appropriate parser based on file MIME type.

        :param file_type: MIME type of the uploaded file.
        :return: Instance of a concrete parsing strategy.
        """
        if file_type == "application/xml":
            return XmlOrderParser()
        elif file_type == "application/json":
            return JsonOrderParser()
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type. Only XML and JSON are supported.")

    def complete_draft_invoice(self, invoice_data: Dict, user_id: str) -> Dict:
        """
        Accepts the user's completed invoice draft and re-validates it.

        :param invoice_data: The updated invoice draft data from the user.
        :param user_id: User identifier (used for draft association).
        :return: Dict indicating success or returning missing fields.
        """
        # Reconstruct the Invoice model from user input
        invoice = Invoice(**invoice_data)
        missing_fields = InvoiceValidator.validate(invoice)

        if missing_fields:
            return {"success": False, "missing_fields": missing_fields}

        # Optional: Store as finalized or trigger downstream processing
        # Example: self._persist_final_invoice(invoice, user_id)

        return {"success": True, "invoice": invoice}
