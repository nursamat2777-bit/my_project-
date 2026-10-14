from app.services.task import TaskService
from sqlachemy.orm import Session
from app.db.session import get_db
from app.services.task import TaskService 


def get_task_service():
    """Функция для инъекции зависимости TaskService"""
    return TaskService(db)