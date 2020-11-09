"""HTML application for DataPosition"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr

# TODO check regularly if pydantic provides a solution
# https://github.com/samuelcolvin/pydantic/issues/1401#issuecomment-670223242
from src.labelled_enum import LabelledEnum
from src.model import load_qa


# RESUME HERE

# TODO
# - [ ] automatically generate a React form from the JSON Schema? https://react-jsonschema-form.readthedocs.io/en/latest/ (for alternatives, see https://json-schema.org/implementations.html#web-ui-generation)
# - [ ] send summary by email? https://pypi.org/project/fastapi-mail/
# - [ ] use the niceties in FastAPI utilities? https://fastapi-utils.davidmontague.xyz/


# model
# TODO move to its own source file
# Profil bâtisseur
# 1 : Savez-vous utiliser une API et requêter des données de manière ponctuelle ou régulière ?
class ChoicesApi(LabelledEnum):
    Api0 = 0, "Je ne sais pas ce qu'est une API"
    Api1 = 1, "Je ne sais pas comment fonctionne une API"
    Api2 = 2, "Je sais ce qu'est une API mais je ne sais pas rédiger une requête."
    Api3 = 3, "Je sais rédiger une requête simple."
    Api4 = 4, "Je crée des connexions via API très régulièrement."


# 2 : ...


class DataPosition(BaseModel):
    # user identification
    name: str = Form(...)
    email: EmailStr = Form(...)
    # profil bâtisseur
    c_api: ChoicesApi = Form(...)


# setup app
app = FastAPI()
templates = Jinja2Templates(directory="templates/")

# form: get
@app.get("/form/")
async def form_get(request: Request):
    return templates.TemplateResponse("form.html", context={"request": request})


# form: post
@app.post("/form/")
async def form_post(
    request: Request,
    *,
    data_position: DataPosition,
):
    return templates.TemplateResponse(
        "summary.html", context={"request": request, "data_position": data_position}
    )
