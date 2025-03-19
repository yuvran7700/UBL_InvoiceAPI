"""
Director for constructing an OrderType object from XML.
Utilizes the OrderXmlExtractor to parse XML and the OrderBuilder to create the final OrderType.
"""

from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.models.invoice import Invoice
from src.order_type_creation.invoice_builder import InvoiceBuilder
from fastapi import HTTPException
import json
import xml.etree.ElementTree as ET

class InvoiceDirector:
    """
    Director class that orchestrates the construction of an Invoice object from XML or JSON.
    """

    @staticmethod
    def construct_invoice_from_data(file_data: bytes, file_extension: str) -> Invoice:
        """
        Constructs an invoice from the provided data (XML or JSON).
        
        Args:
            file_data (bytes): The raw data (either XML or JSON).
            file_extension (str): The type of file ("xml" or "json").
        
        Returns:
            InvoiceType: The constructed invoice.
        
        Raises:
            HTTPException: If the file type is unsupported or data extraction fails.
        """
        # Extract the order data based on the file type (XML or JSON)
        order_data = InvoiceDirector.extract_order_data(file_data, file_extension)
        
        # Use the builder to create the invoice
        invoice_builder = InvoiceBuilder()
        invoice = (
            invoice_builder.set_invoice_id("INV0012345")  # Example ID
            .set_issue_date(order_data["header"]["issue_date"])
            .set_invoice_type_code("380")  # Example invoice type code
            .set_legal_monetary_total(1500.0)  # Example total amount
            .set_due_date(order_data["header"].get("due_date"))
            .set_payment_means(order_data["payment_terms"])
            .set_status("draft")
            .set_invoice_lines(order_data["invoice_lines"])
            .set_header(
                order_reference=order_data["header"]["order_reference"],
                buyer_reference=order_data["header"]["buyer_reference"],
                note=order_data["header"].get("note"),
                document_currency_code="USD"  # Example currency
            )
            .build()
        )
        return invoice

    @staticmethod
    def extract_order_data(file_data: bytes, file_extension: str) -> dict:
        """
        Extracts and standardizes the order data from XML or JSON.
        
        Args:
            file_data (bytes): The raw file data.
            file_extension (str): The file extension ("xml" or "json").
        
        Returns:
            dict: A standardized dictionary containing the order data.
        
        Raises:
            HTTPException: If the file type is unsupported or extraction fails.
        """
        if file_extension == "xml":
            return InvoiceDirector.extract_order_from_xml(file_data)
        elif file_extension == "json":
            return InvoiceDirector.extract_order_from_json(file_data)
        else:
            raise HTTPException(status_code=415, detail="Unsupported file type. Only XML and JSON are supported.")

    @staticmethod
    def extract_order_from_xml(file_data: bytes) -> dict:
        """
        Extracts order data from XML content.
        
        Args:
            file_data (bytes): The raw XML data.
        
        Returns:
            dict: A dictionary containing the extracted order data.
        
        Raises:
            HTTPException: If XML parsing fails or required fields are missing.
        """
        try:
            return OrderXmlUnmarshaller.extract(file_data)  # Extract data using the existing XML extractor
        except ET.ParseError:
            raise HTTPException(status_code=400, detail="Invalid XML content")

    @staticmethod
    def extract_order_from_json(file_data: bytes) -> dict:
        """
        Extracts order data from JSON content.
        
        Args:
            file_data (bytes): The raw JSON data.
        
        Returns:
            dict: A dictionary containing the extracted order data.
        
        Raises:
            HTTPException: If JSON parsing fails or required fields are missing.
        """
        try:
            return json.loads(file_data)  # Parse JSON content
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON content")
