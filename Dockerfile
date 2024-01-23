FROM python:3.9

WORKDIR /app

COPY . /app

RUN pip config set global.index-url http://znana.top:9090/ && pip config set install.trusted-host znana.top && pip install -r requirements.txt

CMD gunicorn main:app -b 0.0.0.0:8981