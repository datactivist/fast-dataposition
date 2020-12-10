# Open questions and references for development

## TODO

### Mandatory

- [ ] bilan : centrer le badge (horizontal)
- [ ] stockage BDD ou airtable, au plus simple pour moi mais il faut un CSV de sortie pour @julia
- [ ] mettre en ligne sur un sous-domaine ou ressource de datactivist.coop
- [ ] position + style bandeau Dataposition - un outil développé par Datactivist (idée Infolab)

### If possible

- [ ] si possible, afficher les questions 1 par 1, éventuellement avec une progress bar
  - javascript: alpaca? [http://www.alpacajs.org/]
  - stocker les réponses dans la session au fur et à mesure : [https://github.com/wtforms/wtforms/issues/250#issuecomment-272004441]

### Speculative

- [ ] drop FastAPI and go with bare Starlette? see eg. [https://www.starlette.io/database/]
- [ ] enable CSRF protection [https://github.com/muicss/starlette-wtf] and [https://wtforms.readthedocs.io/en/2.3.x/csrf/]
- [ ] more natural FastAPI / pydantic, eg. [https://github.com/tiangolo/fastapi/issues/541] or [https://github.com/tiangolo/fastapi/issues/1989], see also [https://amitness.com/2020/06/fastapi-vs-flask/]
- [ ] automatically generate a React form from the JSON Schema? [https://react-jsonschema-form.readthedocs.io/en/latest/] (for alternatives, see [https://json-schema.org/implementations.html#web-ui-generation])
- [ ] send summary by email? [https://pypi.org/project/fastapi-mail/]
- [ ] use the niceties in FastAPI utilities? [https://fastapi-utils.davidmontague.xyz/]
- [ ] check regularly if pydantic provides a solution : [https://github.com/samuelcolvin/pydantic/issues/1401#issuecomment-670223242]

## References

### all together

https://eugeneyan.com/writing/how-to-set-up-html-app-with-fastapi-jinja-forms-templates/
https://github.com/eugeneyan/fastapi-html/blob/master/src/html.py

### fastapi

https://fastapi.tiangolo.com/tutorial/response-model/
https://fastapi.tiangolo.com/tutorial/request-forms/
https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
https://fastapi.tiangolo.com/tutorial/sql-databases/
https://fastapi.tiangolo.com/tutorial/schema-extra-example/

https://fastapi.tiangolo.com/advanced/using-request-directly/

- https://github.com/tiangolo/fastapi/issues/201
- https://github.com/tiangolo/fastapi/issues/852
- https://github.com/tiangolo/fastapi/issues/860

https://python-data-science.readthedocs.io/en/latest/fastapi.html

- https://stackoverflow.com/questions/60971561/how-to-declare-function-with-form-parameters-fastapi-using-pythonway
- https://stackoverflow.com/questions/62386287/fastapi-equivalent-of-flasks-request-form-for-agnostic-forms
- https://stackoverflow.com/questions/61872923/supporting-both-form-and-json-encoded-bodys-with-fastapi
- https://stackoverflow.com/questions/60127234/fastapi-form-data-with-pydantic-model
- https://stackoverflow.com/a/57548509/14201886

## pydantic

https://pydantic-docs.helpmanual.io/usage/schema/
https://stackoverflow.com/questions/43862184/associating-string-representations-with-an-enum-that-uses-integer-values/
https://github.com/samuelcolvin/pydantic/issues/1401#issuecomment-670223242
https://github.com/samuelcolvin/pydantic/issues/637

## starlette

- https://github.com/encode/starlette/blob/master/starlette/templating.py
- https://www.starlette.io/requests/
- https://github.com/muicss/starlette-wtf

## react-jsonschema-form

https://github.com/rjsf-team/react-jsonschema-form/blob/6f7fd11bbf00d37efc7498ea1a38ac53901aa33e/docs/usage/single.md

## HTML

https://www.w3schools.com/tags/att_input_type_radio.asp

## Flask

https://flask.palletsprojects.com/en/1.1.x/patterns/wtforms/
