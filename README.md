# Movie Review System

Дипломний проєкт: **Програмне забезпечення системи аналізу користувацьких відгуків з інтерактивною системою рейтингів для кіноглядачів**.

## Стек технологій

- Backend: Python + FastAPI
- Database: PostgreSQL
- Frontend: HTML / CSS / JavaScript
- ORM: SQLAlchemy

## Структура проєкту

```text
movie-review-system-full/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── utils.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html
```

## Запуск

### 1. Створити базу даних PostgreSQL

Відкрийте pgAdmin або SQL Shell та виконайте:

```sql
CREATE DATABASE movie_reviews_db;
```

### 2. Налаштувати підключення

У папці `backend` створіть файл `.env` на основі `.env.example`.

Приклад:

```text
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/movie_reviews_db
```

### 3. Встановити залежності backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Запустити backend

```bash
uvicorn main:app --reload
```

API буде доступний за адресою:

```text
http://127.0.0.1:8000
```

Документація API:

```text
http://127.0.0.1:8000/docs
```

### 5. Запустити frontend

Відкрийте файл:

```text
frontend/index.html
```

у браузері.

### 6. Почати роботу

1. Натисніть кнопку **Додати тестові дані**.
2. Відкрийте фільм.
3. Додайте відгук.
4. Перейдіть у **Модерація** та змініть статус відгуку.
