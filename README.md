# alfa-hack-credit-cabinet
# Название проекта: Умный кредитный кабинет
Команда:
* Глеб Гусаров - TeamLead / Data Scientist / ML Engineer
* Максимов Алексей - Data Scientist
* Дейнеко Анна - Data Scientist
* Елькин Дмитрий - Frontend developer / Backend developer
* Андрей(блин фамилию забыл) - Frontend developer / Backend developer
Запуск: docker-compose up
Структура:
```text
alfa-hack-credit-cabinet/
│
├── .github/                  # (Опционально) Шаблоны для Issue/PR, если время будет
│
├── backend/                  # Всё, что связано с сервером (Python/FastAPI)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # Точка входа FastAPI (или Streamlit, если выберете его)
│   │   ├── database.py       # Подключение к БД (SQLite/Postgres)
│   │   ├── models.py         # SQLAlchemy модели (таблицы Users, Applications)
│   │   ├── schemas.py        # Pydantic схемы (валидация JSON)
│   │   └── routers/          # Эндпоинты (разбитые по файлам)
│   │       ├── auth.py
│   │       ├── applications.py
│   │       └── products.py
│   ├── requirements.txt      # Зависимости Python (fastapi, uvicorn, sqlalchemy, pandas)
│   └── Dockerfile            # Dockerfile для бэкенда
│
├── frontend/                 # Всё, что связано с интерфейсом
│   ├── src/                  # Исходники (React/Vue/Streamlit)
│   │   ├── components/       # Кнопки, карточки, формы
│   │   ├── pages/            # Экраны (Дашборд, Заявка, Статус)
│   │   └── App.jsx           # Главный компонент (или app.py для Streamlit)
│   ├── package.json          # (Если React/Vue) Зависимости фронта
│   └── Dockerfile            # Dockerfile для фронта (или Nginx)
│
├── ml/                       # ML и Data Science
│   ├── data/                 # Синтетические данные
│   │   ├── raw/              # Исходные сгенерированные CSV (synthetic_companies.csv)
│   │   └── processed/        # Данные после очистки/фичинжиниринга
│   ├── notebooks/            # Jupyter ноутбуки (EDA, обучение модели)
│   │   └── 01_eda_and_model.ipynb
│   ├── src/                  # Python-скрипты для DS
│   │   ├── generate_data.py  # Скрипт генерации синтетики
│   │   ├── mocks.py          # Моки ЕГРЮЛ, ФНС, БКИ
│   │   └── scorer.py         # Класс для загрузки ML-модели и предсказания
│   ├── models/               # Сохраненные веса моделей (model.pkl, catboost.cbm)
│   ├── requirements.txt      # Зависимости для DS (pandas, scikit-learn, faker)
│   └── Dockerfile            # (Опционально) Если ML-сервис отдельный
│
├── docs/                     # Документация (Требование кейса)
│   ├── architecture.png      # Архитектурная схема (рисуете в draw.io)
│   ├── state_diagram.png     # Диаграмма состояний заявки
│   ├── data_model.png        # ER-диаграмма базы данных
│   └── api_spec.json         # Экспорт OpenAPI/Swagger (если не авто)
│
├── tests/                    # Тесты (Хотя бы базовые)
│   ├── test_mocks.py         # Проверка, что моки возвращают правильный JSON
│   └── test_scorer.py        # Проверка, что модель выдает 0 или 1
│
├── .env.example              # Пример переменных окружения (пароли к БД)
├── .gitignore                # Что НЕ загружать в Git (venv, __pycache__, .env, data/raw)
├── docker-compose.yml        # Запуск всего проекта одной командой
├── README.md                 # Главный файл (лицо проекта)
├── THIRD_PARTY_NOTICES.md    # Требование кейса: список сторонних библиотек
└── LICENSE                   # (Опционально) MIT License
