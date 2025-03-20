

from src.marshallers.order_json_unmarshaller_factory import OrderJsonUnmarshaller
from src.marshallers.order_xml_unmarshaller_factory import OrderXmlUnmarshaller
from src.models.invoice import Invoice


class OrderService:
    def construct_invoice_from_data(self, content: bytes, file_type: str) -> Invoice:
        if file_type == "xml":
            unmarshaller = OrderXmlUnmarshaller()
        elif file_type == "json":
            unmarshaller = OrderJsonUnmarshaller()
        else:
            raise ValueError("Unsupported file type")

        header = unmarshaller.unmarshal_header(content)
        supplier_party = unmarshaller.unmarshal_party(content, "SellerSupplierParty")
        customer_party = unmarshaller.unmarshal_party(content, "BuyerCustomerParty")
        invoice_lines = unmarshaller.unmarshal_invoice_lines(content)

        total = sum(line.invoiced_quantity * line.price.get("price_amount", 0.0) for line in invoice_lines)

        return Invoice(
            header=header,
            supplier_party=supplier_party,
            customer_party=customer_party,
            invoice_lines=invoice_lines,
            total={"line_extension_amount": total}
        )
