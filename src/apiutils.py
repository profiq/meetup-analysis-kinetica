import json
import time

import requests


class VerboseMixin:
    LOG_PREFIX = ''

    def _print(self, msg):
        """
        :param str msg: Message to be printed
        """
        assert hasattr(self, '_verbose')
        if self._verbose:
            print('[%s] %s' % (self.LOG_PREFIX, msg.encode().decode(errors='replace')))


class MeetupThrottle(VerboseMixin):
    LOG_PREFIX = 'throttle'

    """
    Meetup.com API allows for only `max_requests` requests during `period` seconds long period of time
    This class can be used to control number of API requests in other parts of code.

    At the time of writing this code the limit was 30 requests per 10 seconds per IP address.

    Example:
        throttle = MeetupThrottle(30, 10)
        while True:
            throttle.wait_for_request_permission()
            ... make your request ...
            throttle.increment_counter()
    """

    def __init__(self, max_requests, period, verbose=False):
        """
        :param int max_requests: Maximum number of requests allowed in during one period
        :param int period: Length of a period in seconds
        :param bool verbose: Print debug information
        """
        self._max_requests = max_requests
        self._period = period
        self._counter = 0
        self._last_period_reset_time = time.time()
        self._verbose = verbose

    def increment_counter(self):
        self._counter += 1
        self._print('Requests in this period: %d' % self._counter)

    def wait_for_request_permission(self):
        if self._counter == self._max_requests:
            self._print('Counter reached maximum')
            time_from_last_reset = time.time() - self._last_period_reset_time
            if time_from_last_reset < self._period:
                self._print('Need to wait until period ends')
                time_to_sleep = self._period - time_from_last_reset
                time.sleep(time_to_sleep)
            self._counter = 0


class CityInfoProvider(VerboseMixin):
    LOG_PREFIX = 'city'

    def __init__(self, endpoint, db, table_name, throttle, verbose=False):
        """
        :param str endpoint: Meetup.com API endpoint URL for getting city info from coordinates
        :param gpudb.GPUdb db: Connection to Kinetica DB
        :param str table_name: Meetup RSVPs table name
        :param MeetupThrottle throttle: Throttle object to manage API request limits
        :param bool verbose: Print debug output
        """
        self._endpoint = endpoint
        self._db = db
        self._table_name = table_name
        self._throttle = throttle
        self._verbose = verbose

    def get_city_for_coordinates(self, event_id, lat, lon):
        """
        :param str event_id:
        :param float lat:
        :param float lon:
        :rtype: str
        """
        if lat is None or lon is None or lat == 0.0 or len == 0.0:
            city = None
        else:
            city = self._find_city_in_db(event_id)
            if city is None:
                city = self._find_city_on_meetup(lat, lon)
        return city

    def _find_city_on_meetup(self, lat: float, lon: float):
        """
        :param float lat:
        :param float lon:
        :rtype: str
        """
        self._throttle.wait_for_request_permission()
        params = {'lat': lat, 'lon': lon, 'page': 1}
        response = requests.get(self._endpoint, params)
        self._throttle.increment_counter()

        if len(response.content) == 0 or response.status_code != 200:
            self._print('Something wrong with the response from meetup.com')
            self._print('Status code: %d' % response.status_code)
            self._print('Text: %s' % response.text)
            self._print('Lat: %.6f, Lon: %.6f' % (lat, lon))
            city = None
        else:
            response_json = response.json()
            if len(response_json['results']) == 1:
                city = response_json['results'][0]['city']
                self._print('City found for lat %.6f and lon %.6f using Meetup API' % (lat, lon))
            else:
                city = None
                self._print('City not found for lat %.6f and lon %.6f' % (lat, lon))
        return city

    def _find_city_in_db(self, event_id):
        """
        :param str event_id:
        :rtype: str
        """
        try:
            results = self._db.get_records(
                self._table_name,
                limit=2,
                encoding='json',
                options={'expression': 'event_id = "%s" AND IS_NULL(city) = 0' % event_id})

            status = results['status_info']
            num_records = len(results['records_json'])

            if status['status'] == 'ERROR':
                self._print('Something went wrong with the DB')
                self._print(status['message'])
                city = None
            elif num_records > 0:
                rsvp_record = json.loads(results['records_json'][0])
                city = rsvp_record['city']
                self._print('City found for event %s in the DB' % event_id)
            else:
                city = None
                self._print('City not found for event %s' % event_id)

        except UnicodeDecodeError:
            city = None

        return city
