"""
Test cases for order upload
Modules Tested: email_field_checker
"""
import pytest
import json

import requests
from src.services.order_service import get_order
from src.utils.external_api_helpers import get_token_order
from src.exceptions.order_exceptions import LoginError, OrderValidationError

@pytest.mark.unit
def test_wrong_id():

    url = "https://code-crusaders-q5k9.onrender.com/v1/user/login"

    body = {
        "email": "alys1.weiss@gmail.com",
        "password": "Password123!"
    }

    try:
        response = requests.post(url, json = body)
        token = (response.json()["token"])
    except:
        raise LoginError()

    with pytest.raises(OrderValidationError) as exc_info:
        get_order(token, 1).run()

    expected_message = '{"error":"Invalid orderId given"}'
    assert exc_info.value.message == expected_message
    assert exc_info.value.status_code == 400