#!/usr/bin/env bash

# Export Dashboard configuration from Reveal
# If you want to access the file you need to mount a folder to /dashboard using Docker
# Dashboard is exported as SQLite DB and stored in /dashboard/dashboard.db in the container

rm /dashboard/dashboard.db
/opt/gpudb/connectors/reveal/lib/python2.7/site-packages/caravel-0.11.0-py2.7.egg/caravel/reveal-utils.py \
    export "Meetup.com Dashboard" /opt/gpudb/connectors/reveal/var/caravel.db /dashboard/dashboard.db