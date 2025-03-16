from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    password: str
    updated_password: str

class UpdateEmailRequest(BaseModel):
    email: EmailStr
    updated_email: EmailStr 

class update_username_request(BaseModel):
    email: EmailStr
    updated_username: str