# 🎬 MovieRate — Система аналізу відгуків та рейтингів фільмів

## 📌 Опис проєкту

MovieRate — це веб-застосунок для аналізу користувацьких відгуків та рейтингів фільмів.
Система дозволяє переглядати фільми, додавати відгуки, оцінювати їх та отримувати статистику.

Проєкт реалізований у вигляді клієнт-серверної архітектури з використанням сучасних технологій.

---

## 🚀 Основний функціонал

* 📽 Перегляд каталогу фільмів
* ⭐ Оцінювання фільмів (рейтинг)
* 💬 Додавання відгуків
* 🧠 Аналіз відгуків (емоційний бал)
* 🔍 Пошук фільмів через TMDb API
* 📊 Перегляд статистики
* 🛠 Модерація контенту
* 👤 Робота з користувачами

---

## 🧱 Архітектура

Система побудована за клієнт-серверною моделлю:

* **Frontend** — HTML, CSS, JavaScript
* **Backend** — Python (FastAPI)
* **База даних** — PostgreSQL
* **Зовнішній API** — TMDb (The Movie Database)

---

## 🌐 Демо (онлайн)

* 🔗 Frontend: https://movie-review-s.netlify.app
* 🔗 Backend API: https://movie-review-backend-5op5.onrender.com
* 🔗 API Docs: https://movie-review-backend-5op5.onrender.com/docs

---

## ⚙️ Встановлення (локально)

### 1. Клонування репозиторію

```bash
git clone https://github.com/your-username/movie-review-system.git
cd movie-review-system
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend

Відкрити файл:

```bash
frontend/index.html
```

---

## 🔑 Налаштування середовища

Створи файл `.env` у папці backend:

```env
DATABASE_URL=your_database_url
TMDB_API_KEY=your_tmdb_api_key
```

---

## 📊 Основні API endpoints

* `GET /tmdb/search` — пошук фільмів
* `GET /tmdb/popular` — популярні фільми
* `POST /tmdb/seed-popular` — додати популярні фільми
* `POST /seed` — заповнити тестові дані
* `GET /stats/reviews` — статистика
* `POST /analysis/recalculate` — аналіз відгуків

---

## 🛠 Технології

* FastAPI
* PostgreSQL
* SQLAlchemy
* JavaScript (Vanilla)
* HTML/CSS
* Chart.js

---

## 👨‍💻 Автор

Савош Олег
Спеціальність: Інженерія програмного забезпечення
НУБіП України

---

## 📌 Примітка

Проєкт створено в рамках дипломної роботи.
Може бути розширений.

---
