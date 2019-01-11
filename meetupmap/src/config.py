import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Meetup.com API endpoints
MEETUP_API_RSVP_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'
MEETUP_API_CITIES_ENDPOINT = 'https://api.meetup.com/2/cities'

# Meetup.com API Limits
MEETUP_MAX_REQUESTS = 30
MEETUP_PERIOD = 10

# Kinetica connection parameters
GPUDB_HOST = 'localhost'
GPUDB_PORT = '9191'

# Definition of a table for storing responses to Meetup events
EVENT_RSVP_COLLECTION = 'meetup'
EVENT_RSVP_TABLE_NAME = 'event_rsvp'

# Table structure definition. Each list describes one column.
# First element of the list defines the column name, the second one the basic data type
# and other elements define additional properties (subtype, indexing).
EVENT_RSVP_TYPE = [
    ['event_id', 'string', 'char32', 'primary_key', 'shard_key'],
    ['name', 'string', 'char128', 'text_search'],
    ['url', 'string', 'char256'],
    ['event_timestamp', 'long', 'nullable', 'timestamp'],
    ['lat', 'double', 'nullable'],
    ['lon', 'double', 'nullable'],
    ['rsvp_id', 'long', 'primary_key'],
    ['response', 'int', 'int8'],
    ['rsvp_timestamp', 'long', 'timestamp'],
    ['city', 'string', 'char64', 'nullable', 'text_search']
]
