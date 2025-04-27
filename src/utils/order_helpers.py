import json
from fastapi import UploadFile

from src.exceptions.order_exceptions import OrderValidationError

def get_json_order(file: UploadFile):
    try:   
        content = file.file.read()
        data = json.loads(content)
        return data
    except:
        raise OrderValidationError("Uploaded file is empty.")
    
    