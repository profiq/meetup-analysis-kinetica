#!/usr/bin/env bash
docker-compose build python
docker-compose up -d
docker-compose logs -f python