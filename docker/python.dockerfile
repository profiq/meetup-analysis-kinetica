FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip

COPY . /app
WORKDIR /app

RUN pip install -r /app/requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "sleep 5 && python /app/src/deploy.py && python /app/src/meetup.py"]