import re
from typing import Optional, Annotated
from datetime import datetime, date

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
    username: Annotated[str, Field(..., min_length=2, max_length=50, description="Нікнейм")]
    password: Annotated[str, Field(..., min_length=8, max_length=50, description="Пароль")]
    email: Annotated[EmailStr, Field(..., min_length=3, max_length=50, description="Email", examples=["useremail@gmail.com"])]


class UserModelResponse(UserModel):
    id: str
    is_active: bool
    role: RoleEnum


class AuthorModel(BaseModel):

    name: Annotated[str, Field(..., min_length=2, max_length=50, description="Ім'я автора")]
    email: Annotated[EmailStr, Field(..., min_length=3, max_length=50, description="Email", examples=["authoremail@gmail.com"])]


class ArticleModel(BaseModel):
    title: Annotated[str, Field(..., min_length=2, max_length=100, description="Заголовок статті")]
    content: Annotated[str, Field(..., min_length=2, description="Контент статті")]
    author: AuthorModel


class ArticleModelResponse(ArticleModel):
    id: str
    author_id: str


class ArticleRequestModel(BaseModel):
    keywords: Annotated[Optional[str], Field(None, description="Ключові слова для пошуку статей", examples=["Python, FastAPI"])]
    date_range: Annotated[Optional[str], Field(None, description="Діапазон дат", examples=["2023-01-01, 2023-12-31"])]


class CommentModel(BaseModel):
    author_name: Annotated[str, Field(..., min_length=2, max_length=50, description="Ім'я автора коментаря")]
    content: Annotated[str, Field(..., min_length=2, description="Контент коментаря")]
    created_at: Annotated[Optional[datetime], Field(default_factory=datetime.now, description="Дата створення коментаря")]


class CommentModelResponse(CommentModel):
    id: str
    article_id: str
    created_at: Annotated[Optional[datetime], Field(default_factory=datetime.now, description="Дата створення коментаря")]