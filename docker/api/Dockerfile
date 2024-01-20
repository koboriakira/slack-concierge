FROM python:3.11-slim

WORKDIR /workspace

# install git
RUN apt update && \
  apt install -y git
RUN apt clean

# Python dependencies
RUN pip install --upgrade pip && \
    pip install pipenv
COPY Pipfile ./
RUN pipenv install --dev
