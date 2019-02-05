FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip

WORKDIR /app
COPY . .

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["/bin/sh", "-c", "sleep 10 && python3 /app/deploy.py && python3 -u /app/meetup.py"]

