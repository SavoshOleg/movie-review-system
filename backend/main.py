from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import requests
import os

import models
import schemas
import crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

with engine.begin() as connection:
    connection.execute(text("ALTER TABLE analysis ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0 NOT NULL"))
    connection.execute(text("ALTER TABLE analysis ADD COLUMN IF NOT EXISTS positivity_percent INTEGER DEFAULT 50 NOT NULL"))
    connection.execute(text("ALTER TABLE movies ADD COLUMN IF NOT EXISTS poster_url TEXT"))

TMDB_API_KEY = "6d577733552255540a5b48c038233cbb"

TMDB_GENRES_UK = {
    28: "Бойовик",
    12: "Пригоди",
    16: "Анімація",
    35: "Комедія",
    80: "Кримінал",
    99: "Документальний",
    18: "Драма",
    10751: "Сімейний",
    14: "Фентезі",
    36: "Історичний",
    27: "Жахи",
    10402: "Музика",
    9648: "Детектив",
    10749: "Романтика",
    878: "Фантастика",
    10770: "Телефільм",
    53: "Трилер",
    10752: "Військовий",
    37: "Вестерн"
}


def genre_names_from_ids(genre_ids):
    names = [TMDB_GENRES_UK.get(gid) for gid in genre_ids or [] if TMDB_GENRES_UK.get(gid)]
    return ", ".join(names) if names else "Фільм"

app = FastAPI(
    title="Movie Review System API",
    description="API для системи аналізу користувацьких відгуків та рейтингів для кіноглядачів",
    version="1.7.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Movie Review System API працює"}


@app.get("/tmdb/search")
def search_tmdb_movies(query: str = Query(..., min_length=1)):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "uk-UA",
        "include_adult": "false"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    results = []
    for movie in data.get("results", [])[:10]:
        release_date = movie.get("release_date") or ""
        poster_path = movie.get("poster_path")

        results.append({
            "tmdb_id": movie.get("id"),
            "title": movie.get("title") or movie.get("original_title") or "Без назви",
            "year": int(release_date[:4]) if release_date[:4].isdigit() else None,
            "description": movie.get("overview") or "Опис відсутній.",
            "genre": genre_names_from_ids(movie.get("genre_ids")),
            "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        })

    return results


@app.get("/tmdb/popular")
def get_popular_tmdb_movies():
    url = "https://api.themoviedb.org/3/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "uk-UA",
        "page": 1
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    results = []
    for movie in data.get("results", [])[:20]:
        release_date = movie.get("release_date") or ""
        poster_path = movie.get("poster_path")

        results.append({
            "tmdb_id": movie.get("id"),
            "title": movie.get("title") or movie.get("original_title") or "Без назви",
            "year": int(release_date[:4]) if release_date[:4].isdigit() else None,
            "description": movie.get("overview") or "Опис відсутній.",
            "genre": genre_names_from_ids(movie.get("genre_ids")),
            "poster_url": f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        })

    return results


@app.post("/tmdb/seed-popular")
def seed_popular_tmdb_movies(db: Session = Depends(get_db)):
    movies = get_popular_tmdb_movies()
    added = 0

    for movie in movies:
        movie_data = schemas.MovieCreate(
            title=movie["title"],
            genre=movie["genre"],
            description=movie["description"],
            year=movie["year"],
            poster_url=movie["poster_url"]
        )
        before = db.query(models.Movie).filter(models.Movie.title == movie["title"]).first()
        crud.create_movie(db, movie_data)
        if not before:
            added += 1

    return {"message": "Популярні фільми TMDb додано", "added": added, "total_loaded": len(movies)}


@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    crud.seed_data(db)
    return {"message": "Тестові дані додано"}


@app.post("/analysis/recalculate")
def recalculate_analysis(db: Session = Depends(get_db)):
    crud.recalculate_old_analysis(db)
    return {"message": "Аналіз відгуків оновлено"}


@app.get("/stats/reviews")
def get_review_stats(db: Session = Depends(get_db)):
    return crud.get_review_stats(db)


@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.UserOut)
def login_user(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.login_user(db, data)
    if not user:
        raise HTTPException(status_code=401, detail="Неправильний email або пароль")
    return user


@app.post("/movies", response_model=schemas.MovieOut)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)


@app.get("/movies", response_model=list[schemas.MovieOut])
def get_movies(db: Session = Depends(get_db)):
    return crud.get_movies(db)


@app.get("/movies/{movie_id}", response_model=schemas.MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    return movie


@app.put("/movies/{movie_id}", response_model=schemas.MovieOut)
def update_movie(movie_id: int, movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    updated_movie = crud.update_movie(db, movie_id, movie)
    if not updated_movie:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    return updated_movie


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_movie(db, movie_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Фільм не знайдено")
    return {"message": "Фільм видалено"}


@app.post("/reviews", response_model=schemas.ReviewOut)
def create_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    if review.rating < 1 or review.rating > 10:
        raise HTTPException(status_code=400, detail="Оцінка має бути від 1 до 10")
    return crud.create_review_with_rating(db, review)


@app.get("/movies/{movie_id}/reviews", response_model=list[schemas.ReviewOut])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    return crud.get_reviews_by_movie(db, movie_id)


@app.get("/users/{user_id}/reviews", response_model=list[schemas.ReviewOut])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)):
    return crud.get_reviews_by_user(db, user_id)


@app.get("/users/{user_id}/recommendations", response_model=list[schemas.MovieOut])
def get_user_recommendations(user_id: int, db: Session = Depends(get_db)):
    return crud.get_recommendations_for_user(db, user_id)


@app.get("/reviews", response_model=list[schemas.ReviewOut])
def get_all_reviews(db: Session = Depends(get_db)):
    return crud.get_all_reviews(db)


@app.patch("/reviews/{review_id}/moderate", response_model=schemas.ReviewOut)
def moderate_review(review_id: int, data: schemas.ModerationUpdate, db: Session = Depends(get_db)):
    review = crud.moderate_review(db, review_id, data)
    if not review:
        raise HTTPException(status_code=404, detail="Відгук не знайдено")
    return review
