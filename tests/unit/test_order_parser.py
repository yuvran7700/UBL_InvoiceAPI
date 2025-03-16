from datetime import date
from src.order_type_builder.order_director import OrderParser

def test_order_parser(sample_order_xml):
    """
    Test that the OrderParser correctly extracts and maps fields from the sample order XML.
    """
    
    # Parse the XML order using the OrderParser.
    order = OrderParser.parse_xml_order(sample_order_xml)

    # Header fields
    assert order.order_id == "AEG012345"
    assert order.sales_order_id == "CON0095678"
    assert order.uuid == "6E09886B-DC6E-439F-82D1-7CCAC7F4E3B1"
    assert order.issue_date == date(2005, 6, 20)
    assert order.note == "sample"

    # Buyer details
    assert order.buyer_account == "XFB01"
    assert order.buyer_name == "IYT Corporation"
    # Check that the formatted buyer address contains key parts.
    assert "Avon Way" in order.buyer_address
    assert "56A" in order.buyer_address
    assert "Bridgtow" in order.buyer_address
    assert "ZZ99 1ZZ" in order.buyer_address
    assert "GB" in order.buyer_address

    # Seller details
    assert order.seller_account == "CO001"
    assert order.seller_name == "Consortial"
    # Check that the formatted seller address contains key parts.
    assert "Busy Street" in order.seller_address
    assert "56A" in order.seller_address
    assert "Farthing" in order.seller_address
    assert "AA99 1BB" in order.seller_address
    assert "GB" in order.seller_address

    # Monetary totals
    assert order.anticipated_line_extension_amount == 100.00
    assert order.anticipated_payable_amount == 100.00

    # Payment terms from TransactionConditions.
    expected_payment_terms = "order response required; payment is by BACS or by cheque"
    assert order.payment_terms == expected_payment_terms

    # Order lines (we expect one order line in the example)
    assert len(order.order_lines) == 1
    line = order.order_lines[0]
    assert line.note == "this is an illustrative order line"
    assert line.line_id == "1"
    assert line.quantity == 100.0
    assert line.line_extension_amount == 100.00
    assert line.total_tax_amount == 17.50
    assert line.unit_price == 100.00
    assert line.item_description == "Acme beeswax"
    assert line.item_name == "beeswax"
    assert line.buyers_item_id == "6578489"
    assert line.sellers_item_id == "17589683"
