from typing import List, Dict, Optional
from uuid import uuid4

from fastapi.routing import APIRouter
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update

from models import get_db, User
from pydantic_models import UserModel, UserModelResponse


users_router = APIRouter(prefix="/users")


async def get_user(token: str = Depends(OAuth2PasswordBearer("/users/token")), db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(token=token)
    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Невірний токен")
    
    return user


@users_router.post("/", status_code=status.HTTP_201_CREATED)
async def add_user(user_model: UserModel, db: AsyncSession = Depends(get_db)):
    user = User(**user_model.model_dump())
    db.add(user)
    await db.commit()


@users_router.post("/token/")
async def get_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    query = select(User).filter_by(username=form_data.username)
    result = await db.execute(query)
    user: Optional[User] = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    if user.password != form_data.password:
        user.token = None
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    token = uuid4().hex
    user.token = token
    await db.commit()
    return {"access_token": token, "token_type": "bearer"}
    