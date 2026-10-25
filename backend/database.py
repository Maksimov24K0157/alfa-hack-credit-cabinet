import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # <-- 1. Импортируем описание таблиц

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("База данных и таблицы успешно созданы!")

if __name__ == "__main__":
    init_db()
