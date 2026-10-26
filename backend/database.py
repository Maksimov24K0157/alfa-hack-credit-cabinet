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

def reset_db():
    """Удаляет файл базы данных, чтобы начать с чистого листа."""
    if os.path.exists("./test.db"):
        os.remove("./test.db")
        print("Файл test.db удален. База данных сброшена.")
    else:
        print("Файла test.db нет, сбрасывать нечего.")

if __name__ == "__main__":
    reset_db()
    init_db()
