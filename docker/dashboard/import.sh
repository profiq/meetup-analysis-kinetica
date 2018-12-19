#!/usr/bin/env bash

# Import Dashboard configuration to Reveal
# Executed when building the Docker image

/opt/gpudb/connectors/reveal/lib/python2.7/site-packages/caravel-0.11.0-py2.7.egg/caravel/reveal-utils.py \
    import "Meetup.com Dashboard"  /dashboard/dashboard.db /opt/gpudb/connectors/reveal/var/caravel.db