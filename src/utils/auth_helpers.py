from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

SECRET_KEY = "a3eddf3292bac4ac269ed39a74e6760ed3c34ff3a15f4cb17c61520da8c88b05"
ALGORITHM = "HS256"
SESSION_EXPIRE_MINUTES = 60
class Token(BaseModel):
    access_token: str
    token_type: str

# Initialize the password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#hash-password helper function 
def hash_password(password: str) -> str:
    """Hash the user's password using bcrypt"""
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = {"email": data["email"]}
    expiration_time = (datetime.now(timezone.utc) + 
                           timedelta(minutes=SESSION_EXPIRE_MINUTES))
    to_encode["expires_at"] = expiration_time.isoformat() 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
    
def decode_token(JWT: str):
    try:
        payload = jwt.decode(JWT, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
