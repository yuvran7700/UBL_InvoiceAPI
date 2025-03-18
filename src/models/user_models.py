from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    business_name: str
    email: EmailStr
    password: str
    abn: str

class UserOut(BaseModel):
    business_name: str
    email: EmailStr
    abn: str    

class UserInDB(BaseModel):
    business_name: str
    email: EmailStr    
    hashed_password: str
    abn: str
    user_id: str

class UpdatePasswordRequest(BaseModel):
    email: EmailStr
    new_password: str

class UpdateUsernameRequest:
    email: EmailStr
    new_business_name: str