"""Pydantic models (schemas)

see https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from typing import List, Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):
    name: str
    color: str
    badge: str


class ProfileCreate(ProfileBase):
    pass


class Profile(ProfileBase):
    id: str

    class Config:
        orm_mode = True


class AnswerBase(BaseModel):
    profile: str
    question: str
    description: str
    weight: int


class AnswerCreate(AnswerBase):
    pass


class Answer(AnswerBase):
    id: int
    author_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    name: str
    selected_profile: Optional[str] = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    answers: List[Answer] = []

    class Config:
        orm_mode = True