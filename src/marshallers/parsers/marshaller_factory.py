from fastapi import HTTPException
from src.marshallers.parsers.invoice_marshaller import InvoiceMarshaller
from src.marshallers.parsers.strategies.json_order_parser import JsonOrderParser
from src.marshallers.parsers.strategies.xml_order_parser import XmlOrderParser

class MarshallerFactory:
    """
    Client class which handles selection and creation of InvoiceMarshaller instances based on file type.
    """

    def create(self, file_type: str) -> InvoiceMarshaller:
        """
        Selects the correct parser strategy explicitly based on file type
        and returns a configured InvoiceMarshaller instance.
        """
        if "xml" in file_type:
            parser = XmlOrderParser()
        elif "json" in file_type:
            parser = JsonOrderParser()
        else:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Only XML and JSON are supported."
            )

        return InvoiceMarshaller(parser)

    def marshal_from_file(self, content: bytes, file_type: str):
        """
        Creates a marshaller, parses and returns invoice directly.
        """
        marshaller = self.create(file_type)
        return marshaller.marshal(content)
