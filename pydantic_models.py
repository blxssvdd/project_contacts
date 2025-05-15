import re
from typing import Optional, Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator
from models import RoleEnum

class ContactModel(BaseModel):
    first_name: Annotated[str, Field(..., min_length=2, max_length=50, description="Ім'я")]
    last_name: Annotated[Optional[str], Field(None, max_length=50, description="Прізвище")]
    email: Annotated[EmailStr, Field(..., min_length=3, max_length=50, description="Email", examples=["email@i.ua"])]
    address: Annotated[Optional[str], Field(None, max_length=150, description="Адреса", examples=["Україна, Київ, вул. Сікорського, буд. 56"])]
    username: Annotated[str, Field(..., min_length=2, max_length=50, description="Нікнейм")]
    phone_number: Annotated[str, Field(..., min_length=18, max_length=18, description="Номер телефону", examples=["+380(66)-123-45-78"])]
    account_id: Annotated[Optional[str], Field(None, description="Посилання на акаунт", examples=["https://t.me/username"])]

    @field_validator("phone_number")
    def phone_number_validate(cls, value: str):
        if re.search(r"\+380\(\d{2}\)-\d{3}-\d{2}-\d{2}", value):
            return value
        raise ValueError("Номер телефону повинен бути записаний у такому форматі: +380(66)-123-45-78")


class ContactModelResponse(ContactModel):
    id: str


class UserModel(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserModelResponse(UserModel):
    id: str
    is_active: bool
    role: RoleEnum