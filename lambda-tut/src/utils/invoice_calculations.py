"""
Module for invoice calculation utilities.

Provides functions for common invoice-related calculations such as computing line extensions,
including handling discounts and additional charges.
"""


def calculate_line_extension(
    quantity: float, unit_price: float, discount: float = 0.0, charge: float = 0.0
) -> float:
    """
    Calculate the line extension amount for an invoice line.

    Args:
        quantity (float): The invoiced quantity.
        unit_price (float): The unit price of the item.
        discount (float, optional): The discount applied to the line. Defaults to 0.0.
        charge (float, optional): The additional charge applied to the line. Defaults to 0.0.

    Returns:
        float: The calculated line extension amount.
    """
    base_amount = quantity * unit_price
    return base_amount - discount + charge
