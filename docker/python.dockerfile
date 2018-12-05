FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip

RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

CMD python src/meetup.py