from typing import Optional, Annotated
from uuid import uuid4

from fastapi import FastAPI, Query, Path, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from models import Contact, get_db, User
from pydantic_models import ContactModel, ContactModelResponse
from users import users_router, get_user

app = FastAPI()
app.include_router(users_router)


@app.post("/contacts/", tags=["Contacts"], summary="Додати новий контакт", status_code=status.HTTP_201_CREATED, response_model=ContactModelResponse)
async def add_contact(
    contact_model: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):

    contact = Contact(**contact_model.model_dump(), id=uuid4().hex)
    db.add(contact)
    await db.commit()
    db.refresh(contact)
    return contact


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)