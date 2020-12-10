"""Database models

Independent from FastAPI or Pydantic.

see https://fastapi.tiangolo.com/tutorial/sql-databases/
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db.base import Base


class Profile(Base):
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    color = Column(String)
    badge = Column(String)

    answers = relationship("Answer", back_populates="profile")


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    selected_profile = Column(String)

    answers = relationship("Answer", back_populates="author")


class Answer(Base):
    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, ForeignKey("profiles.id"))
    question = Column(String, index=True)
    description = Column(String, index=True)
    weight = Column(Integer)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="answers")
    profile = relationship("Profile", back_populates="answers")
