from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.task import TaskORM



class TaskRepository:
    def __init__(self, db: Session) ->None:
        self.db = db

    def get_all(self):
        return self.db.scalars(select(TaskORM)).all()

    def get_by_id(self, task_id:str) -> TaskORM:
        return self.db.get(TaskORM, task_id)

    def create(self, title:str) -> TaskORM: