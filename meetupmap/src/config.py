import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')

# Meetup.com API endpoints
MEETUP_API_RSVP_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'
MEETUP_API_EVENTS_ENDPOINT = 'https://api.meetup.com/2/events'
MEETUP_API_GROUP_ENDPOINT = 'https://api.meetup.com/%s'

# Meetup.com API Limits
MEETUP_API_SLEEP_TIME = 0.35

# Kinetica connection parameters
GPUDB_HOST = 'kinetica'
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
    ['city', 'string', 'char64', 'nullable', 'text_search'],
    ['country', 'string', 'char4', 'nullable'],
    ['group_members', 'long', 'nullable'],
    ['group_events', 'int', 'nullable']
]
