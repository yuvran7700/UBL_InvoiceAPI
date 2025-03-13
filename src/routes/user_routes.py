from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from datetime import datetime
import uuid
from ..models.user import UserCreate, UserUpdate, User
from ..services.dynamodb_service import DynamoDBService

router = APIRouter(prefix="/users", tags=["users"])

# Initialize DynamoDB service
dynamodb_service = DynamoDBService("users")

@router.post("/", response_model=User)
async def create_user(user: UserCreate) -> Dict[str, Any]:
    user_data = user.model_dump()
    user_data.update({
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })
    return dynamodb_service.create_user(user_data)

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str) -> Dict[str, Any]:
    user = dynamodb_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate) -> Dict[str, Any]:
    update_data = user.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    return dynamodb_service.update_user(user_id, update_data)

@router.delete("/{user_id}")
async def delete_user(user_id: str) -> Dict[str, str]:
    if dynamodb_service.delete_user(user_id):
        return {"message": "User deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found") 