from sqlalchemy.orm import Mapped, mapped_column
from base import Base


class TaskORM(Base):#Новый класс который наследует Base
    __tablename__ = "tasks"# С какой именно таблицей связан этот класс

    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
