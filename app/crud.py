"""Interact with the database : Create, Read, Update, and Delete.

Independent from FastAPI or Pydantic.

see https://fastapi.tiangolo.com/tutorial/sql-databases/#crud-utils
"""

from sqlalchemy.orm import Session

from . import models, schemas


# CRUD for users
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def set_user_profile(db: Session, user_id: int, profile: str):
    """Set the selected profile for a user"""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.selected_profile = profile
    db.commit()
    db.refresh(db_user)
    return db_user


# CRUD for answers
def get_answers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Answer).offset(skip).limit(limit).all()


def create_user_answer(db: Session, answer: schemas.AnswerCreate, user_id: int):
    db_answer = models.Answer(**answer.dict(), author_id=user_id)
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


# CRUD for profiles
def get_profiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Profile).offset(skip).limit(limit).all()


def create_profile(db: Session, profile: schemas.ProfileCreate):
    db_profile = models.Profile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile