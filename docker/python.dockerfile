FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python-dev \
    python-pip

COPY . /app
RUN pip install -r /app/requirements.txt
CMD tail -f /dev/null