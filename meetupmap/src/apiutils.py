import requests
import time

from src import config


class EventInfoProvider:

    def __init__(self, db, verbose=False):
        """
        :param gpudb.GPUdb db: Connection to Kinetica DB
        :param bool verbose: Should debug output be printed
        """
        self._db = db
        self._table_name = config.EVENT_RSVP_TABLE_NAME
        self._verbose = verbose

    def get_info(self, event_ids):
        event_ids_str = ','.join(event_ids)
        status, resp = self._do_request(config.MEETUP_API_EVENTS_ENDPOINT, params={'event_id': event_ids_str})
        event_info = {}

        if status == 200:
            events = resp['results']
            for event in events:
                has_city = 'venue' in event and 'city' in event['venue']
                has_country = 'venue' in event and 'country' in event['venue']

                event_info[event['id']] = {
                    'city': event['venue']['city'] if has_city else None,
                    'country': event['venue']['country'] if has_country else None
                }

                group_info = self._get_group_info(event['group']['urlname'])
                event_info[event['id']].update(group_info)

        return event_info

    def _get_group_info(self, urlname):
        params = {'fields': 'past_event_count'}
        status, resp = self._do_request(config.MEETUP_API_GROUP_ENDPOINT % urlname, params=params)
        if status == 200:
            group_info = {
                'group_members': resp['members'] if 'members' in resp else None,
                'group_events': resp['past_event_count'] if 'past_event_count' in resp else None
            }
        else:
            group_info = {'group_members': None, 'group_events': None}
        return group_info

    @staticmethod
    def _do_request(url, params=None):
        params = {} if params is None else params
        params['key'] = '5b5d5233868b12b2d345a4a52f'
        time.sleep(config.MEETUP_API_SLEEP_TIME)
        response = requests.get(url, params)
        return response.status_code, response.json()
