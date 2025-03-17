from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    businessName: str
    email: EmailStr
    password: str
    abn: str

class UserOut(BaseModel):
    businessName: str
    email: EmailStr
    abn: str    

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr


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