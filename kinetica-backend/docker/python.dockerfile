FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip

COPY . /app
WORKDIR /app

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "sleep 5 && python3 /app/meetupmap/deploy.py && python3 -u /app/meetupmap/meetup.py"]
