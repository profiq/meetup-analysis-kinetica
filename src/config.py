import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Kinetica connetcion parameters
GPUDB_HOST = 'kinetica'
GPUDB_PORT = '9191'

# UDF for collecting Meetup.com data
UDF_NAME = 'collect_meetup'
UDF_EXECUTION_MODE = 'nondistributed'

UDF_FILES = {
    'meetup.py': open(os.path.join(SRC_DIR, 'meetup.py'), 'rb').read(),
    'config.py': open(os.path.join(SRC_DIR, 'config.py'), 'rb').read()
}

UDF_COMMAND = 'python'
UDF_ARGS = ['meetup.py']
