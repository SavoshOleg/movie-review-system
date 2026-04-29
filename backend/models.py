from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")

    reviews = relationship("Review", back_populates="user", cascade="all, delete")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete")


class Movie(Base):
    __tablename__ = "movies"

    id_movie = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    genre = Column(String(100), nullable=False)
    description = Column(Text)
    year = Column(Integer)
    poster_url = Column(Text)

    reviews = relationship("Review", back_populates="movie", cascade="all, delete")
    ratings = relationship("Rating", back_populates="movie", cascade="all, delete")


class Review(Base):
    __tablename__ = "reviews"

    id_review = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_movie = Column(Integer, ForeignKey("movies.id_movie", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")
    analysis = relationship("Analysis", back_populates="review", uselist=False, cascade="all, delete")


class Rating(Base):
    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 10", name="check_rating_range"),
    )

    id_rating = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)

    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="CASCADE"), nullable=False)
    id_movie = Column(Integer, ForeignKey("movies.id_movie", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")


class Analysis(Base):
    __tablename__ = "analysis"

    id_analysis = Column(Integer, primary_key=True, index=True)
    sentiment = Column(String(50), nullable=False)
    keywords = Column(Text)
    score = Column(Integer, nullable=False, default=0)
    positivity_percent = Column(Integer, nullable=False, default=50)

    id_review = Column(Integer, ForeignKey("reviews.id_review", ondelete="CASCADE"), unique=True, nullable=False)

    review = relationship("Review", back_populates="analysis")


class Moderation(Base):
    __tablename__ = "moderation"

    id_moderation = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), nullable=False)
    comment = Column(Text)

    id_review = Column(Integer, ForeignKey("reviews.id_review", ondelete="CASCADE"), nullable=False)
    id_user = Column(Integer, ForeignKey("users.id_user"), nullable=False)
