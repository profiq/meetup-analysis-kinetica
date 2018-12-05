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

    rsvp_record = collections.OrderedDict()
    rsvp_record['event_id'] = rsvp['event']['event_id']
    rsvp_record['name'] = rsvp['event']['event_name']
    rsvp_record['url'] = rsvp['event']['event_url']
    rsvp_record['event_timestamp'] = rsvp['event']['time'] if 'time' in rsvp['event'] else None
    rsvp_record['lat'] = rsvp['venue']['lat'] if 'venue' in rsvp else None
    rsvp_record['lon'] = rsvp['venue']['lon'] if 'venue' in rsvp else None
    rsvp_record['rsvp_id'] = rsvp['rsvp_id']
    rsvp_record['response'] = 1 if rsvp['response'] == 'yes' else 0
    rsvp_record['rsvp_timestamp'] = rsvp['mtime']

    response = db.insert_records('event_rsvp', json.dumps(rsvp_record), list_encoding='json')

    if response['status_info']['status'] == 'OK':
        print('RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
    else:
        print('Error while storing')
        print(response)


if __name__ == '__main__':
    main()
