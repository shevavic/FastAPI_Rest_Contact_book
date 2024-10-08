from pydantic import BaseModel, EmailStr, ConfigDict


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    model_config = ConfigDict(from_attributes=True)


class RequestEmail(BaseModel):
    email: EmailStr