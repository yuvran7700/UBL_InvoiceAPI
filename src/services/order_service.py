import requests
from fastapi import UploadFile
from src.utils.external_api_helpers import get_token_order
from src.utils.order_helpers import get_json_order
from src.services.invoice_service_v2 import InvoiceService
from src.exceptions.order_exceptions import InvalidOrderFileError, OrderValidationError, LoginError

invoice_service = InvoiceService()

def order_creation(file: UploadFile, token: str):
    filename = file.filename.lower()
    if filename.endswith(".json"):
        data = get_json_order(file)
    else:
        raise InvalidOrderFileError()

    url = "https://code-crusaders-q5k9.onrender.com/v1/order/create/form"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    order = requests.post(url, headers=headers, json=data)

    if order.status_code == 200:
        return order
    elif order.status_code == 400:
        raise OrderValidationError(order.text)
    elif order.status_code == 401:
        raise LoginError()

def get_order(token: str, order_id: str):
    url = f"https://code-crusaders-q5k9.onrender.com/v1/order/{order_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/xml"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response
    elif response.status_code == 400:
        raise OrderValidationError(response.text)
    elif response.status_code == 401:
        raise LoginError()

def order_to_invoice(file: UploadFile, organisation_id: str, user_id: str):
    token = get_token_order()
    order = order_creation(file, token)
    order_id = order.json().get('orderId')

    if not order_id:
        raise OrderValidationError("No orderId returned from external service.")

    order_res = get_order(token, order_id)
    order_str = order_res.text
    order_bytes = order_str.encode("utf-8")

    invoice = invoice_service.generate_draft_invoice(order_bytes, "application/xml", organisation_id, user_id)
    return invoice
