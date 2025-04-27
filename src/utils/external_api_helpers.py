import requests
from src.exceptions.order_exceptions import LoginError


def get_token_order():

    url = "https://code-crusaders-q5k9.onrender.com/v1/user/login"

    body = {
        "email": "alys1.weiss@gmail.com",
        "password": "Password123!"
    }

    try:
        response = requests.post(url, json = body)
        return(response.json()["token"])
    except:
        raise LoginError()

