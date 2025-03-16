from typing import Optional
from pydantic import BaseModel

class Contact(BaseModel):
    name: str
    telephone: Optional[str] = None
    telefax: Optional[str] = None
    electronic_mail: Optional[str] = None