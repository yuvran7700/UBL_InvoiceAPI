from pydantic import BaseModel, EmailStr, Field


class UserIn(BaseModel):
    business_name: str = Field(...,
                               description="Business name associated with the user.",
                               example="Acme Pty Ltd"
                               )
    email: EmailStr = Field(...,
                            description="Must be a valid email address.",
                            example="user@example.com"
                            )
    password: str = Field(...,
                          min_length=8,
                          description="Must contain at least 8 characters, including one uppercase, one lowercase, and one digit.",
                          example="SecurePass123"
                          )
    abn: str = Field(...,
                     min_length=11,
                     max_length=11,
                     description="Australian Business Number — must be 11 digits and pass ABN validation.",
                     example="51824753556"
                    )



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
    email: EmailStr = Field(...,
                            description="Registered email address of the user.",
                            example="user@example.com"
                            )
    new_password: str = Field(...,
                              min_length=8,
                              description="New password that meets the strength criteria.",
                              example="NewPass123"
                              )

class UpdateUsernameRequest(BaseModel):
    email: EmailStr = Field(...,
                            description="Registered email address of the user.",
                            example="user@example.com"
                            )
    new_business_name: str = Field(...,
                              description="The updated business name for the user.",
                              example="Globex Corporation"
                              )


class UpdateEmailRequest(BaseModel):
    email: EmailStr = Field(...,
                            description="Current email address of the user.",
                            example="user@example.com"
                            )
    new_email: EmailStr = Field(...,
                           description="Current email address of the user.",
                           example="newuser@example.com"
                           )
