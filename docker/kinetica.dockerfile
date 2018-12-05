# Extends basic kinetica intel image
# Automatically adds license key to the config file, so it does not have to be configured in the DB
# Licencse key should be provided as LICENSE_KEY
# DB also starts fully on container start, it doesn't have to be started from Admin interface

FROM kinetica/kinetica-intel

ENV LICENSE_KEY ""
ENV FULL_START 1

COPY kinetica.sh kinetica.sh

ENTRYPOINT ["/bin/bash", "kinetica.sh"]