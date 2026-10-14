from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)#Это связь бд с кодом create_engine создает связь
Sessionlocal = sessionmaker[Session](bind=engine) # Создаём фабрику сессий, которая будет создавать сессии для работы с БД через engine

def get_db():
    """Функция для инъекции БД"""
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
