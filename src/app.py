"""HTML application for DataPosition"""
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, List

from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.templating import Jinja2Templates
from starlette_wtf import StarletteForm
from wtforms import FieldList, SelectField, FormField, StringField
from wtforms.validators import DataRequired, Email

# References:
# https://github.com/muicss/starlette-wtf

# TODO
# - [ ] enable CSRF protection https://wtforms.readthedocs.io/en/2.3.x/csrf/
# - [ ] more natural FastAPI / pydantic, eg. https://github.com/tiangolo/fastapi/issues/541
# - [ ] automatically generate a React form from the JSON Schema? https://react-jsonschema-form.readthedocs.io/en/latest/ (for alternatives, see https://json-schema.org/implementations.html#web-ui-generation)
# - [ ] send summary by email? https://pypi.org/project/fastapi-mail/
# - [ ] use the niceties in FastAPI utilities? https://fastapi-utils.davidmontague.xyz/
# - [ ] check regularly if pydantic provides a solution : https://github.com/samuelcolvin/pydantic/issues/1401#issuecomment-670223242

# from src.labelled_enum import LabelledEnum
from src.model import load_qa, df_to_nesteddict

# the current solution is built after https://stackoverflow.com/a/57548509/14201886

# define the (sub)forms
class QuestionForm(StarletteForm):
    # the content will be filled dynamically from the CSV data :
    # - question (label)
    # - weighted answers (choices)
    # we coerce the form data to int (for the weight)
    # FIXME coercion does not work ?
    question = SelectField("<Question>", choices=[], coerce=int)
    # if we wanted to add a free text field to each question, it would be here


class DatapositionForm(StarletteForm):
    name = StringField("nom", validators=[DataRequired()])
    # https://wtforms.readthedocs.io/en/2.3.x/validators/?highlight=email#wtforms.validators.Email
    email = StringField("email", validators=[DataRequired(), Email()])
    questions = FieldList(FormField(QuestionForm))


# read questions and weighted answers
CSV_QA = "data/qr_databat.csv"
df = load_qa(Path(CSV_QA))
pqwas = df_to_nesteddict(df)


# load the profiles, questions, weights, answers
def get_questions(request: Request) -> List[QuestionForm]:
    """Get forms for questions (and their weighted answers) """
    # for each question, create a subform
    q_forms: List[QuestionForm] = []
    for p, qwa in pqwas.items():
        p_id = p.lower()
        for i, (q, wa) in enumerate(qwa.items(), start=1):
            # assign a distinct id to each question
            q_form_id = f"{p_id}-{i}"
            q_form = QuestionForm(request, prefix=q_form_id)
            q_form.question.label = q
            q_form.question.choices = [(w, a) for w, a in sorted(wa.items())]
            q_forms.append(q_form)
    return q_forms


# setup app
app = FastAPI()
templates = Jinja2Templates(directory="templates/")

# routes
# we directly use the Starlette Request : https://www.starlette.io/requests/
# form: get
@app.get("/form/")
async def get_form(request: Request):
    dataposition_form = DatapositionForm(request)
    dataposition_form.questions = get_questions(request)
    return templates.TemplateResponse(
        "form.html",
        context={"request": request, "dataposition_form": dataposition_form},
    )


# https://github.com/tiangolo/fastapi/issues/852
async def parse_form(request: Request) -> Response:
    form_data = await request.form()
    # TODO store data in DB
    # process form data
    # - compute score for each profile
    p_score: DefaultDict[str, int] = defaultdict(int)
    questions = [(k, v) for k, v in form_data.items() if k.endswith("question")]
    for q_id, w in questions:
        p_id = q_id.split("-", 1)[0]
        p_score[p_id] += int(w)  # FIXME make coerce work
    # TODO radarplot ?
    # return profile summary
    return templates.TemplateResponse(
        "summary.html",
        context={
            "request": request,
            "name": form_data["name"],
            "email": form_data["email"],
            "profile_scores": p_score.items(),
        },
    )


# form: post
@app.post("/form/")
async def submit_answers(summary: Response = Depends(parse_form)):
    return summary
