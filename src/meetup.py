# -*- coding: utf-8 -*-
import functools
import json

import gpudb
import websocket
import collections

import config

MEETUP_API_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    websocket.enableTrace(False)
    on_message = functools.partial(store_rsvp, db=db)
    ws = websocket.WebSocketApp(MEETUP_API_ENDPOINT, on_message=on_message)
    ws.run_forever()


def store_rsvp(_, rsvp_string, db):
    rsvp = json.loads(rsvp_string)
    print('RSVP ID: %d ready to be processed' % rsvp['rsvp_id'])

    event_db_record = collections.OrderedDict()
    event_db_record['event_id'] = rsvp['event']['event_id']
    event_db_record['name'] = rsvp['event']['event_name']
    event_db_record['url'] = rsvp['event']['event_url']
    event_db_record['timestamp'] = rsvp['event']['time'] if 'time' in rsvp['event'] else None
    event_db_record['lat'] = rsvp['venue']['lat'] if 'venue' in rsvp else None
    event_db_record['lng'] = rsvp['venue']['lon'] if 'venue' in rsvp else None

    rsvp_db_record = collections.OrderedDict()
    rsvp_db_record['rsvp_id'] = rsvp['rsvp_id']
    rsvp_db_record['response'] = 1 if rsvp['response'] == 'yes' else 0
    rsvp_db_record['timestamp'] = rsvp['mtime']
    rsvp_db_record['event_id'] = rsvp['event']['event_id']

    response_rsvp = db.insert_records('rsvp', json.dumps(rsvp_db_record), list_encoding='json')
    response_event = db.insert_records('event', json.dumps(event_db_record), list_encoding='json')

    if response_rsvp['status_info']['status'] == 'OK' and response_event['status_info']['status'] == 'OK':
        print('RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
    else:
        print('Error while storing')
        print(response_rsvp)
        print(response_event)


if __name__ == '__main__':
    main()