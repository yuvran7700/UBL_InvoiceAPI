"""
Pydantic models for user registration, log in and log out.
Includes registration reequest, session request and logout request.
"""

from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    """
    Represents a register request to create a new account.

    Attributes:
        businessName (str): Users business name.
        email (EmailStr): Users email to login.
        password (str): Password of user to log in.
        abn (str): Users Australian Business Number
    """
    businessName: str
    email: EmailStr
    password: str
    abn: str


class SessionRequest(BaseModel):

    """
    Represents a session requests for logging in.

    Attributes:
        email (EmailStr): Users email to login.
        password (str): Password of user to log in.
    """

    email: EmailStr
    password: str


class LogOutRequest(BaseModel):

    """
    Represents a requests for logging out.

    Attributes:
        JWT (str): Encoded Json web token.
    """

    JWT: str
