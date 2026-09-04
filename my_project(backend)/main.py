from uuid import uuid4
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session


DATABASE_URL = "postgresql+psycopg://postgres:admin@127.0.0.1:15432/postgres" # Подключение к бд
engine = create_engine(DATABASE_URL)#Это связь бд с кодом create_engine создает связь
Sessionlocal = sessionmaker[Session](bind=engine) # Создаём фабрику сессий, которая будет создавать сессии для работы с БД через engine


class Base(DeclarativeBase):#Ну новый класс который создает экземпляр на основе DeclarativeBase
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid4()))#
#

class TaskORM(Base):#Новый класс который наследует Base
    __tablename__ = "tasks"# С какой именно таблицей связан этот класс

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind = engine)
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

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


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
def create_book(payload:BookWrite, db: Session = Depends(get_db)):
    global book
    book = payload.book
    return book

@app.get("/book")
def fav_book(db: Session = Depends(get_db)):
    return f"Любимая книга: {book}"

def task_orm_to_model(task_orm: TaskORM):
    return TaskSchema(id = task_orm.id, title = task_orm.title, completed = task_orm.completed)


@app.get("/tasks")  # Если придёт GET-запрос на /tasks, вызвать функцию ниже
def read_tasks(db: Session = Depends(get_db)) -> list[TaskSchema]: # FastAPI вызывает get_db(), получает сессию БД и передаёт её в переменную db. Функция должна вернуть список TaskSchema
    tasks_from_db = db.scalars(select(TaskORM)).all() # Получаем из БД все записи таблицы tasks, как объекты TaskORM и сохраняем их в список tasks_from_db
    return [task_orm_to_model(task) for task in tasks_from_db]

@app.post("/tasks", status_code= 201)
def create_task(payload: TaskCreateSchema, db: Session = Depends(get_db) ) -> TaskSchema :
    new_task = TaskORM(title = payload.title, completed = False)
    db.add(new_task)
    db.commit()
    return task_orm_to_model(task_for_update)

@app.patch("/tasks/{task_id}")
def update_task(task_id: str, payload: TaskUpdateSchema, db: Session = Depends(get_db)):
    task_for_update = db.get(TaskORM, task_id)
    if payload.title:
        task_for_update.title = payload.title
    if payload.completed:
        task_for_update.completed = payload.completed

    db.commit()
    return task_for_update

@app.delete("/tasks/{task_id}", status_code = 204)
def delete_task(task_id, db: Session = Depends(get_db)):
    task_for_delete = db.get(TaskORM, task_id)
    db.delete(task_for_delete)
    db.commit()


@app.get("/categories")
def read_categories(db: Session = Depends(get_db)):
    return categories

@app.post("/categories", status_code = 201)
def add_categories(payload:CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category( id = str(uuid4()), name = payload.name)
    categories.append(new_category)
    return new_category

@app.patch("/categories/{category_id}")
def r_categories(category_id, payload: CategoryUpdate, db: Session = Depends(get_db)):
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
def delete_cat(category_id, db: Session = Depends(get_db)):
    for category in categories:
        if category.id == category_id:
            categories.remove(category)
            return
    raise HTTPException(
        status_code=404,
        detail="Category not found"
    )
