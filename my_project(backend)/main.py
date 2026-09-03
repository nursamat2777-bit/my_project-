from uuid import uuid4
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres" # Подключение к бд
engine = create_engine(DATABASE_URL)#Это связь бд с кодом create_engine создает связь
Sessionlocal = sessionmaker[Session](bind=engine)#создание какого то шаблона для создания сессии


class Base(DeclarativeBase):#Ну новый класс который создает экземпляр на основе DeclarativeBase
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))#
#

class TaskORM(Base):#Новый класс который наследует Base
    __tablename__ = "tasks"#
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all()
    yield

app = FastAPI(lifespan = lifespan)

book = ""

categories = []

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_methods=["*"],
)

class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool

tasks: list[TaskSchema] = []

class TaskCreateSchema(BaseModel):
    title: str

class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None

class BookWrite(BaseModel):
    book: str

class Category(BaseModel):
    id: str
    name: str

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):

    name: str | None = None


@app.post("/book")
def create_book(payload:BookWrite):
    global book
    book = payload.book
    return book

@app.get("/book")
def fav_book():
    return f"Любимая книга: {book}"

@app.get("/tasks")
def read_tasks() -> list[TaskSchema]:
    return tasks

@app.post("/tasks", status_code= 201)
def create_task(payload: TaskCreateSchema) -> TaskSchema :
    new_task = TaskSchema(id = str(uuid4()), title = payload.title, completed= False)

    tasks.append(new_task)
    return new_task

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema):
    for task in tasks:
        if task.id == task_id:
            if payload.title:
                task.title = payload.title
            if payload.completed is not None:
                task.completed = payload.completed
            return task

@app.delete("/tasks/{task_id}", status_code = 204)
def delete_task(task_id):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)


@app.get("/categories")
def read_categories():
    return categories

@app.post("/categories", status_code = 201)
def add_categories(payload:CategoryCreate):
    new_category = Category( id = str(uuid4()), name = payload.name)
    categories.append(new_category)
    return new_category

@app.patch("/categories/{category_id}")
def r_categories(category_id, payload: CategoryUpdate):
    for category in categories:
        if category.id == category_id:
            if payload.name is not None:
                category.name = payload.name
            return category

    raise HTTPException(
        status_code=404,
        detail="Категория не найдена"
    )


@app.delete("/categories/{category_id}", status_code=204)
def delete_cat(category_id):
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return
    raise HTTPException(
        status_code=404,
        detail="Category not found"
    )
