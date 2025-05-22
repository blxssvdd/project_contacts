from typing import Optional, Annotated
from uuid import uuid4
from sqlalchemy import select
from datetime import datetime, date
import logging
import asyncio

# datetime.now()

from fastapi import FastAPI, Query, Path, HTTPException, status, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from models import Contact, get_db, User, Article, Comment
from pydantic_models import ContactModel, ContactModelResponse, UserModel, UserModelResponse, ArticleModel, ArticleModelResponse, ArticleRequestModel, CommentModel, CommentModelResponse
from users import users_router, get_user

app = FastAPI()
app.include_router(users_router)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_middleware")


@app.middleware("http")
async def test_middleware(request: Request, call_next) -> Response:
    x_custom_header = request.headers.get("X-Custom-Header")
    if not x_custom_header:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Заголовок 'X-Custom-Header' є обов'язковим")


    response: Response = await call_next(request)


    time_end = str(datetime.now())
    logger.info(f"Визвали функцію {call_next} за допомогою методу {request.method} {request.url} за {datetime.now()} с.")
    response.headers["Execute-time"] = str(time_end)

    return response



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


@app.get("/contacts/", tags=["Contacts"], summary="Отримати список контактів", response_model=list[ContactModelResponse])

async def get_contacts(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    result = await db.execute(select(Contact))
    contacts = result.scalars().all()
    return contacts


@app.get("/contacts/{contact_id}", tags=["Contacts"], summary="Отримати контакт за ID", response_model=ContactModelResponse)
async def get_contact(
    contact_id: str = Path(..., min_length=1, max_length=100, description="ID контакту"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Contact).filter_by(id=contact_id)
    result = await db.execute(query)
    contact: Optional[Contact] = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")

    return contact


@app.delete("/contacts/{contact_id}", tags=["Contacts"], summary="Видалити контакт за ID", status_code=status.HTTP_200_OK)
async def delete_contact(
    contact_id: str = Path(..., min_length=1, max_length=100, description="ID контакту"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Contact).filter_by(id=contact_id)
    result = await db.execute(query)
    contact: Optional[Contact] = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Контакт не знайдено")

    await db.delete(contact)
    await db.commit()
    return {"detail": "Контакт успішно видалено"}



@app.post("/articles/", tags=["Articles"], summary="Додати нову статтю", status_code=status.HTTP_201_CREATED, response_model=ArticleModelResponse)
async def add_article(
    article_model: ArticleModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    article = Article(**article_model.model_dump(), id=uuid4().hex)
    db.add(article)
    await db.commit()
    return article


@app.get("/articles/", tags=["Articles"], summary="Отримати список статей", response_model=list[ArticleModelResponse])
async def get_articles(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    result = await db.execute(select(Article))
    articles = result.scalars().all()
    return articles


@app.get("/articles/{article_id}", tags=["Articles"], summary="Отримати статтю за ID", response_model=ArticleModelResponse)
async def get_article(
    article_id: str = Path(..., min_length=1, max_length=100, description="ID статті"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Article).filter_by(id=article_id)
    result = await db.execute(query)
    article: Optional[Article] = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стаття не знайдена")

    return article


@app.delete("/articles/{article_id}", tags=["Articles"], summary="Видалити статтю за ID", status_code=status.HTTP_200_OK)
async def delete_article(
    article_id: str = Path(..., min_length=1, max_length=100, description="ID статті"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Article).filter_by(id=article_id)
    result = await db.execute(query)
    article: Optional[Article] = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Стаття не знайдена")

    await db.delete(article)
    await db.commit()
    return {"detail": "Стаття успішно видалена"}



@app.get("/articles/search/", tags=["Articles"], summary="Пошук статей по ключовому слову", response_model=list[ArticleModelResponse])
async def search_articles(
    keyword: str = Query(..., min_length=1, max_length=100, description="Ключове слово для пошуку"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    
    text = f"%{keyword}%"
    query = select(Article).filter(Article.content.like(text))
    result = await db.execute(query)
    articles = result.scalars().all()
    if not articles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статті не знайдені")
    return articles



@app.get("/articles/filter/", tags=["Articles"], summary="Фільтрація статей по даті", response_model=list[ArticleModelResponse])
async def filter_articles_by_date(
    date_start: datetime = Query(..., description="Початкова дата (YYYY-MM-DD)"),
    date_end: datetime = Query(..., description="Кінцева дата (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    
    query = select(Article).filter(Article.created_at > date_start).filter(Article.created_at < date_end)
    result = await db.execute(query)
    articles = result.scalars().all()
    if not articles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статті не знайдені")
    return articles



@app.post("/comments/", tags=["Comments"], summary="Додати новий коментар", status_code=status.HTTP_201_CREATED, response_model=CommentModelResponse)
async def add_comment(
    comment_model: CommentModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    comment = Comment(**comment_model.model_dump(), id=uuid4().hex)
    db.add(comment)
    await db.commit()
    db.refresh(comment)
    return comment


@app.get("/comments/", tags=["Comments"], summary="Отримати список коментарів", response_model=list[CommentModelResponse])
async def get_comments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    result = await db.execute(select(Comment))
    comments = result.scalars().all()
    return comments


@app.get("/comments/{comment_id}", tags=["Comments"], summary="Отримати коментар за ID", response_model=CommentModelResponse)
async def get_comment(
    comment_id: str = Path(..., min_length=1, max_length=100, description="ID коментаря"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Comment).filter_by(id=comment_id)
    result = await db.execute(query)
    comment: Optional[Comment] = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Коментар не знайдено")

    return comment


@app.delete("/comments/{comment_id}", tags=["Comments"], summary="Видалити коментар за ID", status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: str = Path(..., min_length=1, max_length=100, description="ID коментаря"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_user)
):
    query = select(Comment).filter_by(id=comment_id)
    result = await db.execute(query)
    comment: Optional[Comment] = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Коментар не знайдено")

    await db.delete(comment)
    await db.commit()
    return {"detail": "Коментар успішно видалено"}




if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)


#INFOHUB