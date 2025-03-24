

from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.models.invoice import Invoice


class OrderService:


 #total = sum(line.invoiced_quantity * line.price.get("price_amount", 0.0) for line in invoice_lines)