from typing import Optional
from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[int]):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    patronymic: Optional[str] = None
    role_id: int
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: EmailStr
    password: str
    role_id: int
    first_name: str
    last_name: str
    patronymic: Optional[str] = ""
    is_send_notify: Optional[bool] = False
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
