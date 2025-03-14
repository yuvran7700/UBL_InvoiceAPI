from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str