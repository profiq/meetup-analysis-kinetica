import collections
import functools
import json
import traceback

import gpudb
import requests
import websocket

import apiutils
import config


class CityInfoProvider:

    def __init__(self, endpoint: str, db: gpudb.GPUdb, table_name: str, throttle: apiutils.MeetupThrottle,
                 verbose=False):
        self._endpoint = endpoint
        self._db = db
        self._verbose = verbose
        self._table_name = table_name
        self._throttle = throttle

    def get_city_for_coordinates(self, event_id: str, lat: float, lon: float) -> str:
        if lat is None or lon is None:
            city = None
        else:
            city = self._find_city_in_db(event_id)
            if city is None:
                city = self._find_city_on_meetup(lat, lon)
        return city

    def _find_city_on_meetup(self, lat: float, lon: float) -> str:
        self._throttle.wait_for_request_permission()
        params = {'lat': lat, 'lon': lon, 'page': 1}
        response = requests.get(self._endpoint, params).json()
        self._throttle.increment_counter()
        if 'results' in response and len(response['results']) == 1:
            city = response['results'][0]['city']
        else:
            city = None
        return city

    def _find_city_in_db(self, event_id: str) -> str:
        city = None

        try:
            results = self._db.get_records(
                self._table_name,
                limit=2,
                encoding='json',
                options={'expression': 'event_id = "%s" AND IS_NULL(city) = 0' % event_id})
        except UnicodeDecodeError:
            return None

        status = results['status_info']
        num_records = len(results['records_json'])

        if num_records > 0:
            rsvp_record = json.loads(results['records_json'][0])
            city = rsvp_record['city']

        if self._verbose:
            if num_records == 0:
                print('Event with city not found, need to use Meetup API')
            elif num_records > 0:
                print('City found in the DB')
        if status['status'] == 'ERROR':
            raise Exception(status['message'])

        return city


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    throttle = apiutils.MeetupThrottle(config.MEETUP_MAX_REQUESTS, config.MEETUP_PERIOD)
    city_info_provider = CityInfoProvider(
        config.MEETUP_API_CITIES_ENDPOINT, db, config.EVENT_RSVP_TABLE_NAME, throttle, True)
    websocket.enableTrace(False)
    on_message = functools.partial(store_rsvp, db=db, city_info_provider=city_info_provider)
    ws = websocket.WebSocketApp(config.MEETUP_API_RSVP_ENDPOINT, on_message=on_message)
    ws.run_forever()


def store_rsvp(_, rsvp_string, db, city_info_provider: CityInfoProvider):
    try:
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
        rsvp_record['city'] = city_info_provider.get_city_for_coordinates(
            rsvp_record['event_id'], rsvp_record['lat'], rsvp_record['lon'])

        response = db.insert_records('event_rsvp', json.dumps(rsvp_record, ensure_ascii=False), list_encoding='json')

        if response['status_info']['status'] == 'OK':
            print('RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
        else:
            print('Error while storing')
            print(response)
    except Exception as e:
        print(traceback.format_exc())
        raise e


if __name__ == '__main__':
    while True:
        main()
