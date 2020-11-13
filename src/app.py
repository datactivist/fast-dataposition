"""HTML application for DataPosition"""
from collections import defaultdict
from pathlib import Path
from random import shuffle
from typing import DefaultDict, List

from fastapi import FastAPI, Depends, Request, Form, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette_wtf import StarletteForm
from wtforms import FieldList, RadioField, FormField, StringField
from wtforms.validators import DataRequired, Email

# References:
# - https://github.com/tiangolo/fastapi/issues/852
# - https://stackoverflow.com/a/57548509/14201886
# - https://github.com/muicss/starlette-wtf

# TODO
# - [ ] enable CSRF protection https://github.com/muicss/starlette-wtf and https://wtforms.readthedocs.io/en/2.3.x/csrf/
# - [ ] more natural FastAPI / pydantic, eg. https://github.com/tiangolo/fastapi/issues/541 or https://github.com/tiangolo/fastapi/issues/1989
#       see also https://amitness.com/2020/06/fastapi-vs-flask/
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
    question = RadioField("<Question>", choices=[], coerce=int)
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

# profiles: id, name, color, badge
profiles = [
    ("ambassadeur", "Ambassadeur", "#6EA0CC", "dataposition_ambassadeur.png"),
    ("analyste", "Analyste", "#E46480", "dataposition_analyste.png"),
    ("batisseur", "Bâtisseur", "#7A6CB6", "dataposition_batisseur.png"),
    ("creatif", "Créatif", "#FF604A", "dataposition_creatif.png"),
    ("expert", "Expert", "#46C39B", "dataposition_expert.png"),
    ("pilote", "Pilote", "#FBCF1A", "dataposition_pilote.png"),
]
p_name2id = {p_name: p_id for p_id, p_name, _, _ in profiles}
p_id2name = {p_id: p_name for p_id, p_name, _, _ in profiles}
p_id2badge = {p_id: p_badge for p_id, _, _, p_badge in profiles}
p_id2color = {p_id: p_color for p_id, _, p_color, _ in profiles}

# load the profiles, questions, weights, answers
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
    for p, qwa in pqwas.items():
        p_id = p_name2id[p]
        for i, (q, wa) in enumerate(qwa.items(), start=1):
            # assign a distinct id to each question
            q_form_id = f"{p_id}-{i}"
            q_form = QuestionForm(request, prefix=q_form_id)
            q_form.question.label = q
            q_form.question.choices = [(w, a) for w, a in sorted(wa.items())]
            q_forms.append(q_form)
    # randomize the order of questions
    if order == "shuffle":
        shuffle(q_forms)
    return q_forms


# setup app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")

# routes
# we directly use the Starlette Request : https://www.starlette.io/requests/
# see https://fastapi.tiangolo.com/advanced/using-request-directly/?h=+using+requ#use-the-request-object-directly
# form: get
@app.get("/")
async def get_form(request: Request):
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


# TODO
# - ajouter le logo de datactivist dans le bandeau (footer?)
# - ajouter un logo du concours d'innovation (header?)
# - stockage BDD ou airtable, au plus simple pour moi mais il faut un CSV de sortie pour @julia
# - mettre en ligne sur un sous-domaine ou ressource de datactivist.coop
# - si possible, afficher les questions 1 par 1, éventuellement avec une progress bar
#    + javascript: alpaca? http://www.alpacajs.org/
#    + stocker les réponses dans la session au fur et à mesure : https://github.com/wtforms/wtforms/issues/250#issuecomment-272004441
# FIXME
# - enlever les guillemets autour des questions et réponses
# - style des questions: couleur du profil autour de question + réponses (background? box?)
# - position + style bandeau Dataposition - un outil développé par Datactivist

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
    # return profile summary
    return templates.TemplateResponse(
        "summary.html",
        context={
            "request": request,
            "p_id2color": p_id2color,
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
