from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: str
    additional_data: Optional[str] = None


class ContactUpdateSchema(ContactSchema):
    completed: bool


class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: str
    additional_data: Optional[str] = None
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None
    model_config = ConfigDict(from_attributes=True)