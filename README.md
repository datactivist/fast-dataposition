# fast-dataposition

Questionnaires dataposition avec FastAPI

# 1. Installation

## 1.1 Local Installation using Docker

Prerequisite :
`docker`, `docker-compose`

Clone this repository :

```sh
git clone https://github.com/datactivist/fast-dataposition.git
cd fast-dataposition
```

Create a new .env file containing :

```sh
# to enable alembic to find app
PYTHONPATH=.
# SQLite
SQLITE_DB=dataposition
```

Create the docker image and run the container :

```sh
docker-compose build
docker-compose up
```

It should be accessible at http://localhost


## 1.2 Local Installation /TODO

1. Install poetry [https://python-poetry.org/docs/]
```sh
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

1. Go to your folder and init poetry
```sh
poetry init
```

1. Add the dependencies, during init or after :
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



## 2. Deployment on a server with SSL encryption

Make your docker container run on port 8000, to let nginx use port 80 (here we use nano, but use your preffered command line editor) :

```sh
nano fast-dataposition/docker-compose.yml
```

change the line from `"80:80"` to `"8000:80"`


Install nginx :

```sh
sudo apt update
sudo apt install nginx
```

Add your nginx configuration:

```sh
sudo nano /etc/nginx/sites-available/example.your-domain.com
```

The file should contain :
```NGINX
server {
        listen 80;
        listen [::]:80;

        index index.html index.htm index.nginx-debian.html;

        server_name example.your-domain.com www.example.your-domain.com;

        location / {
                location / {
                proxy_pass http://localhost:8000;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                try_files $uri $uri/ =404;
        }
}
```

Activate your nginx configuration :
```sh
sudo ln -s /etc/nginx/sites-available/example.your-domain.com /etc/nginx/sites-enabled/
```

check that your nginx configuration is correct :
```sh
sudo nginx -t
```

Now install certbot : 
```sh
sudo apt install certbot python3-certbot-nginx
```

Obtain an ssl certificate using cerbot and let's encrypt :
```sh
sudo certbot --nginx -d example.your-domain.com -d www.example.your-domain.com
```
and follow the prompts.

You can now restart nginx :
```sh
sudo systemctl restart nginx
```