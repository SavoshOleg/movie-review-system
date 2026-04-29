from sqlalchemy.orm import Session
from sqlalchemy import func
import models
import schemas
from utils import hash_password, analyze_sentiment


def fill_review_analysis(review):
    if review.analysis:
        review.sentiment = review.analysis.sentiment
        review.keywords = review.analysis.keywords
        review.score = review.analysis.score
        review.positivity_percent = review.analysis.positivity_percent
    else:
        review.sentiment = None
        review.keywords = None
        review.score = 0
        review.positivity_percent = 50
    return review


def fill_movie_rating(db: Session, movie):
    average = db.query(func.avg(models.Rating.rating)).filter(models.Rating.id_movie == movie.id_movie).scalar()
    movie.average_rating = round(float(average), 2) if average else 0
    return movie


def create_user(db: Session, user: schemas.UserCreate):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        return existing
    db_user = models.User(name=user.name, email=user.email, password_hash=hash_password(user.password), role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def login_user(db: Session, data: schemas.UserLogin):
    password_hash = hash_password(data.password)
    return db.query(models.User).filter(models.User.email == data.email, models.User.password_hash == password_hash).first()


def create_movie(db: Session, movie: schemas.MovieCreate):
    existing = db.query(models.Movie).filter(models.Movie.title == movie.title).first()
    if existing:
        if movie.poster_url and not existing.poster_url:
            existing.poster_url = movie.poster_url
            db.commit()
            db.refresh(existing)
        return fill_movie_rating(db, existing)

    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    db_movie.average_rating = 0
    return db_movie


def update_movie(db: Session, movie_id: int, movie: schemas.MovieCreate):
    db_movie = db.query(models.Movie).filter(models.Movie.id_movie == movie_id).first()
    if not db_movie:
        return None
    db_movie.title = movie.title
    db_movie.genre = movie.genre
    db_movie.description = movie.description
    db_movie.year = movie.year
    db_movie.poster_url = movie.poster_url
    db.commit()
    db.refresh(db_movie)
    return fill_movie_rating(db, db_movie)


def delete_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id_movie == movie_id).first()
    if not db_movie:
        return False
    db.delete(db_movie)
    db.commit()
    return True


def get_movies(db: Session):
    movies = db.query(models.Movie).order_by(models.Movie.id_movie).all()
    for movie in movies:
        fill_movie_rating(db, movie)
    return movies


def get_movie(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id_movie == movie_id).first()
    if movie:
        fill_movie_rating(db, movie)
    return movie


def create_review_with_rating(db: Session, review: schemas.ReviewCreate):
    db_review = models.Review(text=review.text, id_user=review.id_user, id_movie=review.id_movie, status="pending")
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    db_rating = models.Rating(rating=review.rating, id_user=review.id_user, id_movie=review.id_movie)
    db.add(db_rating)

    sentiment, keywords, score, positivity_percent = analyze_sentiment(review.text)
    db_analysis = models.Analysis(sentiment=sentiment, keywords=keywords, score=score, positivity_percent=positivity_percent, id_review=db_review.id_review)
    db.add(db_analysis)

    db.commit()
    db.refresh(db_review)

    db_review.sentiment = sentiment
    db_review.keywords = keywords
    db_review.score = score
    db_review.positivity_percent = positivity_percent
    return db_review


def get_reviews_by_movie(db: Session, movie_id: int):
    reviews = db.query(models.Review).filter(models.Review.id_movie == movie_id).order_by(models.Review.id_review.desc()).all()
    for review in reviews:
        fill_review_analysis(review)
    return reviews


def get_reviews_by_user(db: Session, user_id: int):
    reviews = db.query(models.Review).filter(models.Review.id_user == user_id).order_by(models.Review.id_review.desc()).all()
    result = []
    for review in reviews:
        fill_review_analysis(review)
        review.movie_title = review.movie.title if review.movie else "Невідомий фільм"
        result.append(review)
    return result


def get_all_reviews(db: Session):
    reviews = db.query(models.Review).order_by(models.Review.id_review.desc()).all()
    for review in reviews:
        fill_review_analysis(review)
    return reviews


def moderate_review(db: Session, review_id: int, data: schemas.ModerationUpdate):
    review = db.query(models.Review).filter(models.Review.id_review == review_id).first()
    if not review:
        return None
    review.status = data.status
    moderation = models.Moderation(status=data.status, comment=data.comment, id_review=review_id, id_user=data.id_moderator)
    db.add(moderation)
    db.commit()
    db.refresh(review)
    fill_review_analysis(review)
    return review


def recalculate_old_analysis(db: Session):
    reviews = db.query(models.Review).all()
    for review in reviews:
        sentiment, keywords, score, positivity_percent = analyze_sentiment(review.text)
        if review.analysis:
            review.analysis.sentiment = sentiment
            review.analysis.keywords = keywords
            review.analysis.score = score
            review.analysis.positivity_percent = positivity_percent
        else:
            db.add(models.Analysis(sentiment=sentiment, keywords=keywords, score=score, positivity_percent=positivity_percent, id_review=review.id_review))
    db.commit()


def get_review_stats(db: Session):
    reviews = db.query(models.Review).all()
    total = len(reviews)
    positive = 0
    neutral = 0
    negative = 0
    pending = 0
    approved = 0
    rejected = 0
    positivity_sum = 0

    for review in reviews:
        fill_review_analysis(review)
        if review.sentiment == "Позитивний":
            positive += 1
        elif review.sentiment == "Негативний":
            negative += 1
        else:
            neutral += 1

        if review.status == "pending":
            pending += 1
        elif review.status == "approved":
            approved += 1
        elif review.status == "rejected":
            rejected += 1

        positivity_sum += review.positivity_percent or 50

    average_positivity = round(positivity_sum / total, 1) if total else 0

    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "average_positivity": average_positivity
    }


def get_recommendations_for_user(db: Session, user_id: int):
    user_ratings = db.query(models.Rating).filter(models.Rating.id_user == user_id).all()
    watched_movie_ids = {rating.id_movie for rating in user_ratings}
    liked_genres = {}

    for rating in user_ratings:
        if rating.rating >= 7 and rating.movie:
            liked_genres[rating.movie.genre] = liked_genres.get(rating.movie.genre, 0) + rating.rating

    user_reviews = db.query(models.Review).filter(models.Review.id_user == user_id).all()
    for review in user_reviews:
        if review.analysis and review.analysis.sentiment == "Позитивний" and review.movie:
            liked_genres[review.movie.genre] = liked_genres.get(review.movie.genre, 0) + 3

    if liked_genres:
        sorted_genres = sorted(liked_genres.items(), key=lambda item: item[1], reverse=True)
        preferred_genres = [genre for genre, _ in sorted_genres]
        movies = db.query(models.Movie).filter(~models.Movie.id_movie.in_(watched_movie_ids), models.Movie.genre.in_(preferred_genres)).all()
        recommendations = []
        for movie in movies:
            fill_movie_rating(db, movie)
            movie.recommendation_reason = f"Рекомендовано, бо вам подобається жанр: {movie.genre}"
            recommendations.append(movie)
        recommendations.sort(key=lambda movie: (preferred_genres.index(movie.genre), -movie.average_rating))
        return recommendations[:8]

    movies = db.query(models.Movie).all()
    recommendations = []
    for movie in movies:
        if movie.id_movie not in watched_movie_ids:
            fill_movie_rating(db, movie)
            movie.recommendation_reason = "Популярний фільм з каталогу"
            recommendations.append(movie)
    recommendations.sort(key=lambda movie: movie.average_rating, reverse=True)
    return recommendations[:8]


def seed_data(db: Session):
    users = [
        models.User(name="Олег", email="oleg@example.com", password_hash=hash_password("123456"), role="user"),
        models.User(name="Марина", email="maryna@example.com", password_hash=hash_password("123456"), role="user"),
        models.User(name="Адміністратор", email="admin@example.com", password_hash=hash_password("123456"), role="admin"),
        models.User(name="Модератор", email="moderator@example.com", password_hash=hash_password("123456"), role="moderator"),
    ]

    for user in users:
        exists = db.query(models.User).filter(models.User.email == user.email).first()
        if not exists:
            db.add(user)

    movies = [
        ("Дюна: Частина друга", "Фантастика", "Продовження історії Пола Атріда та боротьби за Арракіс.", 2024, "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg"),
        ("Інтерстеллар", "Фантастика", "Науково-фантастична історія про подорож крізь космос.", 2014, "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"),
        ("Оппенгеймер", "Драма", "Біографічна драма про створення атомної бомби.", 2023, "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"),
        ("Матриця", "Фантастика", "Культовий фільм про симуляцію реальності.", 1999, "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"),
        ("Джокер", "Драма", "Психологічна драма про становлення складного персонажа.", 2019, "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg"),
        ("Темний лицар", "Бойовик", "Кримінальний бойовик про протистояння Бетмена та Джокера.", 2008, "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"),
        ("Початок", "Трилер", "Фільм про сни, реальність і складні рівні свідомості.", 2010, "https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg"),
        ("Аватар", "Фантастика", "Фантастична історія про світ Пандори та його мешканців.", 2009, "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg"),
        ("Форрест Ґамп", "Драма", "Історія життя доброго і щирого героя на тлі важливих подій.", 1994, "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"),
        ("Джон Вік 4", "Бойовик", "Динамічний бойовик із великою кількістю екшен-сцен.", 2023, "https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg"),
        ("Соціальна мережа", "Драма", "Фільм про створення Facebook та розвиток технологічного бізнесу.", 2010, "https://image.tmdb.org/t/p/w500/n0ybibhJtQ5icDqTp8eRytcIHJx.jpg"),
        ("Гра в імітацію", "Драма", "Історія Алана Тюрінга та розшифрування коду Енігма.", 2014, "https://image.tmdb.org/t/p/w500/zSqJ1qFq8NXFfi7JeIYMlzyR0dx.jpg"),
    ]

    for title, genre, description, year, poster_url in movies:
        exists = db.query(models.Movie).filter(models.Movie.title == title).first()
        if not exists:
            db.add(models.Movie(title=title, genre=genre, description=description, year=year, poster_url=poster_url))
        else:
            updated = False
            if poster_url and not exists.poster_url:
                exists.poster_url = poster_url
                updated = True
            if genre and exists.genre == "TMDb":
                exists.genre = genre
                updated = True
            if updated:
                db.add(exists)

    db.commit()
    recalculate_old_analysis(db)
