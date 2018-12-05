import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Kinetica connection parameters
GPUDB_HOST = 'kinetica-my'
GPUDB_PORT = '9191'

# Table definition for storing responses to Meetup events
EVENT_RSVP_COLLECTION = 'meetup'
EVENT_RSVP_TABLE_NAME = 'event_rsvp'

EVENT_RSVP_TYPE = [
    ['event_id', 'string', 'char32', 'primary_key', 'shard_key'],
    ['name', 'string', 'char128', 'text_search'],
    ['url', 'string', 'char128'],
    ['event_timestamp', 'long', 'nullable', 'timestamp'],
    ['lat', 'double', 'nullable'],
    ['lon', 'double', 'nullable'],
    ['rsvp_id', 'long', 'primary_key'],
    ['response', 'int', 'int8'],
    ['rsvp_timestamp', 'long', 'timestamp']
]


# UDF for collecting Meetup.com data
UDF_NAME = 'collect_meetup'
UDF_EXECUTION_MODE = 'nondistributed'

UDF_FILES = {
    'meetup.py': open(os.path.join(SRC_DIR, 'meetup.py'), 'rb').read(),
    'config.py': open(os.path.join(SRC_DIR, 'config.py'), 'rb').read()
}

UDF_COMMAND = 'python'
UDF_ARGS = ['meetup.py']
