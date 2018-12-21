# Extends basic kinetica intel image
# Automatically adds license key to the config file, so it does not have to be configured in the DB
# Licencse key should be provided as LICENSE_KEY
# Meetup.com dashboard for Reveal is imported during build
# DB also starts fully on container start, it doesn't have to be started from Admin interface

FROM kinetica/kinetica-intel:6.2.0

ENV LICENSE_KEY ""
ENV FULL_START 1

COPY kinetica.sh kinetica.sh
COPY dashboard /dashboard
RUN bash /dashboard/import.sh

ENTRYPOINT ["/bin/bash", "kinetica.sh"]
