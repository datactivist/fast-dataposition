"""HTML application for DataPosition

References :
- https://stackoverflow.com/a/57548509/14201886
- https://fastapi.tiangolo.com/tutorial/sql-databases/#main-fastapi-app
"""
from collections import defaultdict
import json
from pathlib import Path
from random import shuffle
from typing import DefaultDict, List

from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette_wtf import StarletteForm
from wtforms import FieldList, RadioField, FormField, StringField
from wtforms.validators import DataRequired, Email

from . import crud, models, schemas
from .db.session import SessionLocal, engine
from .pqwa_csv import load_pqwa, df_to_nesteddict

#
# define the (sub)forms
class QuestionForm(StarletteForm):
    # the content will be filled dynamically from the CSV data :
    # - question (label)
    # - weighted answers (choices)
    # we coerce the form data to int (for the weight)
    # FIXME coercion does not work ?
    # FIXME DataRequired does not work ? https://github.com/wtforms/wtforms/issues/477
    question = RadioField(
        "<Question>", choices=[], coerce=int, validators=[DataRequired()]
    )
    # if we wanted to add a free text field to each question, it would be here


class DatapositionForm(StarletteForm):
    name = StringField("nom", validators=[DataRequired()])
    # https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=email#wtforms.validators.Email
    email = StringField("email", validators=[DataRequired(), Email()])
    questions = FieldList(FormField(QuestionForm))


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# read profiles, questions and weighted answers
# FIXME move out to config file
JSON_PROFILES = "data/profiles.json"
CSV_PQWA = "data/qr_databat.csv"

# FIXME move out to another config file
PQWA_NAMES = ["Profil", "Question", "Pondération (1 à 4)", "Valeur de réponse"]

# profiles: id, name, color, badge
with open(Path(JSON_PROFILES)) as f_profiles:
    profiles = json.load(f_profiles)

# PQWA
df = load_pqwa(Path(CSV_PQWA), PQWA_NAMES)
pqwas = df_to_nesteddict(df)

# maps from/to profile id
p_name2id = {p["name"]: p["id"] for p in profiles}
p_id2name = {p["id"]: p["name"] for p in profiles}
p_id2badge = {p["id"]: p["badge"] for p in profiles}
p_id2color = {p["id"]: p["color"] for p in profiles}

# load the profiles, questions, weights, answers
# FIXME refactor to put the list of questions in the DataBase,
# with their own table and proper IDs etc
list_questions = []
for p, qwa in pqwas.items():
    p_id = p_name2id[p]
    for i, (q, wa) in enumerate(qwa.items(), start=1):
        # assign a distinct id to each question
        q_form_id = f"{p_id}-{i}"
        q_label = q
        q_choices = [(w, a) for w, a in sorted(wa.items())]
        list_questions.append((q_form_id, q_label, q_choices))
qid2q = {q_form_id: q_label for q_form_id, q_label, _ in list_questions}
qid2w2a = {
    q_form_id: {w: a for w, a in q_choices}
    for q_form_id, _, q_choices in list_questions
}
# end FIXME


def get_questions(request: Request, order: str = "keep") -> List[QuestionForm]:
    """Get forms for questions (and their weighted answers)

    Parameters
    ----------
    request
        Starlette request.
    order
        Order of the questions: "keep" their order of appearance in the file or "shuffle" them.
    """
    if order not in ("keep", "shuffle"):
        raise ValueError("Possible values : 'keep', 'shuffle'")
    # for each question, create a subform
    q_forms: List[QuestionForm] = []
    for q_form_id, q_label, q_choices in list_questions:
        q_form = QuestionForm(request, prefix=q_form_id)
        q_form.question.label = q_label
        q_form.question.choices = q_choices
        # select the lowest value as the default answer
        q_form.question.data = q_form.question.choices[0][0]
        q_forms.append(q_form)
    # randomize the order of questions
    if order == "shuffle":
        shuffle(q_forms)
    return q_forms


# create all tables in database
# comment this out if you're not using migrations (alembic)
# models.Base.metadata.create_all(bind=engine)

# setup app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")

# routes
# we directly use the Starlette Request : https://www.starlette.io/requests/
# see https://fastapi.tiangolo.com/advanced/using-request-directly/?h=+using+requ#use-the-request-object-directly
# form: get
@app.get("/")
async def get_form(request: Request, db: Session = Depends(get_db)):
    # create profiles if none in the database
    db_profiles = crud.get_profiles(db)
    if not db_profiles:
        # empty table
        for profile in profiles:
            # DIRTY copy from crud.create_profile()
            db_profile = models.Profile(**profile)
            db.add(db_profile)
            db.commit()
            db.refresh(db_profile)
    # end create profiles if none

    # build form
    dataposition_form = DatapositionForm(request)
    dataposition_form.questions = get_questions(request, order="shuffle")
    return templates.TemplateResponse(
        "form.html",
        context={
            "request": request,
            "dataposition_form": dataposition_form,
            "p_id2color": p_id2color,
        },
    )


# parse form
# as starlette's request.form() is asynchronous, we need to wrap receiving the data
# from the form, in a separate dependency
# https://github.com/tiangolo/fastapi/issues/852
async def parse_form(request: Request, db: Session = Depends(get_db)) -> Response:
    form_data = await request.form()
    # store data in DB
    # - user info
    user_name = form_data["name"]
    user_email = form_data["email"]
    # check if a user with this email already exists
    existing_user = (
        db.query(models.User).filter(models.User.email == user_email).first()
    )
    if existing_user:
        # update the name
        existing_user.name = user_name
        # delete previous answers
        existing_answers = db.query(models.Answer).filter(
            models.Answer.author_id == existing_user.id
        )
        existing_answers.delete(synchronize_session=False)
        db_user = existing_user
    else:
        # insert new user
        # FIXME copy from create_user
        db_user = models.User(email=user_email, name=user_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # end FIXME

    # - answers (DIRTY)
    form_qid_w = [
        (k.replace("-question", ""), int(v))
        for k, v in form_data.items()
        if k.endswith("question")
    ]
    prep_answers = [
        {
            "profile_id": k.split("-", 1)[0],
            "question": qid2q[k],
            "weight": v,
            "description": qid2w2a[k][v],
        }
        for k, v in form_qid_w
    ]
    for prep_answer in prep_answers:
        db_answer = models.Answer(**prep_answer, author_id=db_user.id)
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)

    # process form data
    # - compute score for each profile
    p_score: DefaultDict[str, int] = defaultdict(int)
    questions = [(k, v) for k, v in form_data.items() if k.endswith("question")]
    for q_id, w in questions:
        p_id = q_id.split("-", 1)[0]
        p_score[p_id] += int(w)  # FIXME make coerce work on form validation
    print(p_score.items())  # DEBUG
    # TODO radarplot ?
    # sort profiles by their score
    sorted_profiles = list(sorted(p_score.items(), key=lambda pw: pw[1], reverse=True))
    # assign main profiles : currently the argmax of the scores
    max_score = sorted_profiles[0][1]
    main_p_ids = [p_id for p_id, w in sorted_profiles if w == max_score]
    main_profiles = [p_id2name[p_id] for p_id in main_p_ids]
    main_colors = [p_id2color[p_id] for p_id in main_p_ids]
    main_badges = [p_id2badge[p_id] for p_id in main_p_ids]

    # store user badge(s) ; union of badges if there is a tie
    # TODO improve on this
    db_user.selected_profile = "|".join(main_profiles)
    db.commit()
    db.refresh(db_user)
    # end store user badge(s)

    # return profile summary
    return templates.TemplateResponse(
        "summary.html",
        context={
            "request": request,
            "p_id2color": p_id2color,
            "p_id2name": p_id2name,
            # personal info
            "name": form_data["name"],
            "email": form_data["email"],
            # score for each profile (sorted in descending order)
            "profile_scores": sorted_profiles,
            # main profiles
            # FIXME pass less info, or better structured
            "main_p_ids": main_p_ids,
            "main_profiles": main_profiles,
            "main_colors": main_colors,
            "main_badges": main_badges,
        },
    )


# form: post
@app.post("/")
async def submit_answers(summary: Response = Depends(parse_form)):
    return summary


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/answers/", response_model=schemas.Answer)
def create_answer_for_user(
    user_id: int, answer: schemas.AnswerCreate, db: Session = Depends(get_db)
):
    return crud.create_user_answer(db=db, answer=answer, user_id=user_id)


@app.get("/answers/", response_model=List[schemas.Answer])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_answers(db, skip=skip, limit=limit)
    return items