from decimal import Decimal
from datetime import date

def convert_floats_to_decimal_helper(obj):
    """
    Recursively convert float values in a structure (dict or list)
    to Decimal objects.
    
    Args:
        obj: The input structure (float, dict, or list).
    
    Returns:
        The structure with all float values converted to Decimal.
    """
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal_helper(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal_helper(item) for item in obj]
    else:
        return obj

def convert_dates_helper(obj):
    """
    Recursively convert date objects in a structure (dict or list)
    to ISO formatted strings.
    
    Args:
        obj: The input structure (date, dict, or list).
    
    Returns:
        The structure with all date objects converted to ISO strings.
    """
    if isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_dates_helper(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_helper(item) for item in obj]
    else:
        return obj

def convert_data_for_dynamodb(data: dict) -> dict:
    """
    Convert a dictionary so that all date fields become ISO strings
    and all float values become Decimal objects, which are required by DynamoDB.
    
    Args:
        data (dict): The original data dictionary.
    
    Returns:
        dict: The converted data dictionary.
    """
    data = convert_dates_helper(data)
    data = convert_floats_to_decimal_helper(data)
    return data
