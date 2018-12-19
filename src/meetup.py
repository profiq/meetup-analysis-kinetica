import collections
import functools
import json
import traceback

import gpudb
import websocket

import apiutils
import config


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    throttle = apiutils.MeetupThrottle(config.MEETUP_MAX_REQUESTS, config.MEETUP_PERIOD)
    city_info_provider = apiutils.CityProvider(
        config.MEETUP_API_CITIES_ENDPOINT, db, config.EVENT_RSVP_TABLE_NAME, throttle)
    websocket.enableTrace(False)
    on_message = functools.partial(store_rsvp, db=db, city_info_provider=city_info_provider)
    ws = websocket.WebSocketApp(config.MEETUP_API_RSVP_ENDPOINT, on_message=on_message)
    ws.run_forever()


def store_rsvp(_, rsvp_string, db, city_info_provider: apiutils.CityProvider):
    try:
        rsvp = json.loads(rsvp_string)
        print('[stream] RSVP ID: %d ready to be processed' % rsvp['rsvp_id'])

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
        rsvp_record['city'] = city_info_provider.get_city(
            rsvp_record['event_id'], rsvp_record['lat'], rsvp_record['lon'])

        response = db.insert_records('event_rsvp', json.dumps(rsvp_record, ensure_ascii=False), list_encoding='json')

        if response['status_info']['status'] == 'OK':
            print('[stream] RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
        else:
            print('[stream] Error while storing')
            print(response)
    except Exception as e:
        print(traceback.format_exc())
        raise e


if __name__ == '__main__':
    while True:
        main()
