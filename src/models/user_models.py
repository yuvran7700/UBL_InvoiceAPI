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
    user_id: str
    email: EmailStr
    business_name: str
    abn: str
    hashed_password: str