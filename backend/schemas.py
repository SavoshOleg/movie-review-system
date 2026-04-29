from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "user"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id_user: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class MovieCreate(BaseModel):
    title: str
    genre: str
    description: Optional[str] = None
    year: Optional[int] = None
    poster_url: Optional[str] = None


class MovieOut(BaseModel):
    id_movie: int
    title: str
    genre: str
    description: Optional[str]
    year: Optional[int]
    poster_url: Optional[str] = None
    average_rating: float = 0
    recommendation_reason: Optional[str] = None

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    text: str
    rating: int
    id_user: int
    id_movie: int


class ReviewOut(BaseModel):
    id_review: int
    text: str
    status: str
    id_user: int
    id_movie: int
    sentiment: Optional[str] = None
    keywords: Optional[str] = None
    score: Optional[int] = 0
    positivity_percent: Optional[int] = 50
    movie_title: Optional[str] = None

    class Config:
        from_attributes = True


class ModerationUpdate(BaseModel):
    status: str
    comment: Optional[str] = None
    id_moderator: int
