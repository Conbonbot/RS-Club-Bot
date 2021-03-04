FROM python:3.7-slim-buster

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
