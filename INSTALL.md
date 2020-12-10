# Installation

## On a local machine

1. Install poetry [https://python-poetry.org/docs/]
```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

2. Go to your folder and init poetry
```sh
poetry init
```

3. Add the dependencies, during init or after :
```sh
poetry add fastapi
poetry add alembic
poetry add -D black
poetry add -D pytest
poetry add -D flake8
```

`-D` marks dependencies useful for development but not production.

4. 

```sh
# if necessary
sudo service docker start
# build docker image
docker build -t img-dataposition .
# launch the container locally
docker run -d --name ctr-dataposition -p 80:80 img-dataposition
```

5. Create database with alembic

```sh
export PYTHONPATH=$PYTHONPATH:.
alembic revision --autogenerate -m "Create profiles, users, questions tables"
alembic upgrade head
```

## Deploy on the server