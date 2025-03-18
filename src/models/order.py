from pydantic import BaseModel
from typing import Optional, Dict

class OrderUploadRequest(BaseModel):
    ubl_file_format: str  # "xml" or "json"
    additional_inputs: Optional[Dict[str, str]] = {}

class ParsedOrderResponse(BaseModel):
    missing_fields: List[str]
    extracted_data: Dict[str, str]
