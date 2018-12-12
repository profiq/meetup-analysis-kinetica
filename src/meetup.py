import collections
import functools
import json

import gpudb
import requests
import websocket

import config

MEETUP_API_RSVP_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'
MEETUP_API_CITIES_ENDPOINT = 'https://api.meetup.com/2/cities'


class CityInfoProvider:

    def __init__(self, endpoint: str, db: gpudb.GPUdb):
        self._endpoint = endpoint
        self._db = db

    def get_city_for_coordinates(self, lat: float, lon: float) -> str:
        params = {'lat': lat, 'lon': lon, 'page': 1}
        response = requests.get(self._endpoint, params).json()
        if len(response['results']) == 1:
            city = response['results'][0]['city']
        else:
            city = None
        return city


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    city_info_provider = CityInfoProvider(MEETUP_API_CITIES_ENDPOINT, db)
    websocket.enableTrace(False)
    on_message = functools.partial(store_rsvp, db=db, city_info_provider=city_info_provider)
    ws = websocket.WebSocketApp(MEETUP_API_RSVP_ENDPOINT, on_message=on_message)
    ws.run_forever()


def store_rsvp(_, rsvp_string, db, city_info_provider: CityInfoProvider):
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
    rsvp_record['city'] = city_info_provider.get_city_for_coordinates(rsvp_record['lat'], rsvp_record['lon'])

    response = db.insert_records('event_rsvp', json.dumps(rsvp_record), list_encoding='json')

    if response['status_info']['status'] == 'OK':
        print('RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
    else:
        print('Error while storing')
        print(response)


if __name__ == '__main__':
    main()
