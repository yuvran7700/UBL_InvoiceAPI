from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr
    new_email: EmailStr 