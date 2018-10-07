FROM python:latest
LABEL author="acatejr@gmail.com"
EXPOSE 8000

RUN apt-get update -y --fix-missing

WORKDIR /opt/app
COPY . /opt/app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
