# marshallers/exporters/strategies/xml_exporter.py
import xml.dom.minidom
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree, register_namespace
from src.domain.models.invoice_update import InvoiceUpdateModel
from src.marshallers.exporters.strategies.invoice_export_strategy import InvoiceExportStrategy

UBL_NS = "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
CAC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
CBC_NS = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"

NSMAP = {"cac": CAC_NS, "cbc": CBC_NS}

# Register global XML namespaces
register_namespace("cac", CAC_NS)
register_namespace("cbc", CBC_NS)

class XmlInvoiceFormatter(InvoiceExportStrategy):
    def serialize(self, invoice: InvoiceUpdateModel) -> bytes:
        invoice_el = Element("Invoice", xmlns=UBL_NS)

        def cbc(tag, text):
            el = SubElement(invoice_el, f"{{{CBC_NS}}}{tag}")
            el.text = str(text)
            return el

        def cac(tag):
            return SubElement(invoice_el, f"{{{CAC_NS}}}{tag}")

        # Top-level fields
        cbc("UBLVersionID", "2.1")
        cbc("CustomizationID", invoice.customization_id)
        cbc("ProfileID", invoice.profile_id)
        cbc("ID", invoice.id)
        cbc("IssueDate", invoice.issue_date)
        cbc("InvoiceTypeCode", invoice.invoice_type_code)
        cbc("DocumentCurrencyCode", invoice.document_currency_code)
        if invoice.due_date:
            cbc("DueDate", invoice.due_date)
        if invoice.buyer_reference:
            cbc("BuyerReference", invoice.buyer_reference)

        # OrderReference
        if invoice.order_reference and invoice.order_reference.id:
            order_ref = cac("OrderReference")
            SubElement(order_ref, f"{{{CBC_NS}}}ID").text = invoice.order_reference.id

        # Supplier
        if invoice.accounting_supplier_party:
            supp_party = cac("AccountingSupplierParty")
            party = SubElement(supp_party, f"{{{CAC_NS}}}Party")

            if invoice.accounting_supplier_party.party_name:
                name_el = SubElement(party, f"{{{CAC_NS}}}PartyName")
                SubElement(name_el, f"{{{CBC_NS}}}Name").text = invoice.accounting_supplier_party.party_name.name

            if invoice.accounting_supplier_party.postal_address:
                addr = SubElement(party, f"{{{CAC_NS}}}PostalAddress")
                SubElement(addr, f"{{{CBC_NS}}}StreetName").text = invoice.accounting_supplier_party.postal_address.street_name
                SubElement(addr, f"{{{CBC_NS}}}CityName").text = invoice.accounting_supplier_party.postal_address.city_name
                SubElement(addr, f"{{{CBC_NS}}}PostalZone").text = invoice.accounting_supplier_party.postal_address.postal_zone
                if invoice.accounting_supplier_party.postal_address.country:
                    country = SubElement(addr, f"{{{CAC_NS}}}Country")
                    SubElement(country, f"{{{CBC_NS}}}IdentificationCode").text = invoice.accounting_supplier_party.postal_address.country.identification_code

        # Customer
        if invoice.accounting_customer_party:
            cust_party = cac("AccountingCustomerParty")
            party = SubElement(cust_party, f"{{{CAC_NS}}}Party")

            if invoice.accounting_customer_party.party_name:
                name_el = SubElement(party, f"{{{CAC_NS}}}PartyName")
                SubElement(name_el, f"{{{CBC_NS}}}Name").text = invoice.accounting_customer_party.party_name.name

            if invoice.accounting_customer_party.postal_address:
                addr = SubElement(party, f"{{{CAC_NS}}}PostalAddress")
                SubElement(addr, f"{{{CBC_NS}}}StreetName").text = invoice.accounting_customer_party.postal_address.street_name
                SubElement(addr, f"{{{CBC_NS}}}CityName").text = invoice.accounting_customer_party.postal_address.city_name
                SubElement(addr, f"{{{CBC_NS}}}PostalZone").text = invoice.accounting_customer_party.postal_address.postal_zone
                if invoice.accounting_customer_party.postal_address.country:
                    country = SubElement(addr, f"{{{CAC_NS}}}Country")
                    SubElement(country, f"{{{CBC_NS}}}IdentificationCode").text = invoice.accounting_customer_party.postal_address.country.identification_code

        # Monetary Total
        if invoice.legal_monetary_total:
            monetary = cac("LegalMonetaryTotal")
            SubElement(monetary, f"{{{CBC_NS}}}LineExtensionAmount", currencyID=invoice.document_currency_code).text = str(invoice.legal_monetary_total.line_extension_amount)
            SubElement(monetary, f"{{{CBC_NS}}}TaxExclusiveAmount", currencyID=invoice.document_currency_code).text = str(invoice.legal_monetary_total.tax_exclusive_amount)
            SubElement(monetary, f"{{{CBC_NS}}}TaxInclusiveAmount", currencyID=invoice.document_currency_code).text = str(invoice.legal_monetary_total.tax_inclusive_amount)
            SubElement(monetary, f"{{{CBC_NS}}}PayableAmount", currencyID=invoice.document_currency_code).text = str(invoice.legal_monetary_total.payable_amount)

        # Invoice Lines
        if invoice.invoice_lines:
            for line in invoice.invoice_lines:
                line_el = cac("InvoiceLine")
                SubElement(line_el, f"{{{CBC_NS}}}ID").text = line.id
                SubElement(line_el, f"{{{CBC_NS}}}InvoicedQuantity", unitCode=line.unit_code).text = str(line.invoiced_quantity)
                SubElement(line_el, f"{{{CBC_NS}}}LineExtensionAmount", currencyID=invoice.document_currency_code).text = str(line.line_extension_amount)

                # Item
                if line.item:
                    item_el = SubElement(line_el, f"{{{CAC_NS}}}Item")
                    SubElement(item_el, f"{{{CBC_NS}}}Name").text = line.item.name
                    if line.item.classified_tax_category:
                        tax_cat = SubElement(item_el, f"{{{CAC_NS}}}ClassifiedTaxCategory")
                        SubElement(tax_cat, f"{{{CBC_NS}}}ID").text = line.item.classified_tax_category.id
                        SubElement(tax_cat, f"{{{CBC_NS}}}Percent").text = str(line.item.classified_tax_category.percent)
                        SubElement(tax_cat, f"{{{CAC_NS}}}TaxScheme").append(SubElement(Element(""), f"{{{CBC_NS}}}ID", text=line.item.classified_tax_category.tax_scheme_id))

                # Price
                if line.price:
                    price_el = SubElement(line_el, f"{{{CAC_NS}}}Price")
                    SubElement(price_el, f"{{{CBC_NS}}}PriceAmount", currencyID=invoice.document_currency_code).text = str(line.price.price_amount)

        # Return XML string
        rough_string = tostring(invoice_el, encoding="utf-8", xml_declaration=True)
        parsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding="utf-8")
        return pretty_xml
