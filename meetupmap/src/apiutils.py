import requests
import time
import json

from src import config


class EventInfoProvider:

    def __init__(self, db):
        """
        :param gpudb.GPUdb db: Connection to Kinetica DB
        """
        self._db = db
        self._table_name = config.EVENT_RSVP_TABLE_NAME

    def get_info(self, event_ids):
        event_info = self._get_event_info_from_db(event_ids)
        print('[event] DB hits: %d' % len(event_info))
        event_ids_not_in_db = [e for e in event_ids if e not in event_info]
        event_info.update(self._get_info_from_meetup(event_ids_not_in_db))
        print('[event] Meetup hits: %d' % len(event_ids_not_in_db))
        return event_info

    def _get_info_from_meetup(self, event_ids):
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

    def _get_event_info_from_db(self, event_ids):
        event_ids_str = "'%s'" % "','".join(event_ids)
        try:
            event_info = {}
            results = self._db.aggregate_group_by(
                table_name=self._table_name,
                column_names=['event_id', 'city', 'country', 'group_members', 'group_events'],
                encoding='json',
                offset=0,
                options={
                    'expression': 'event_id IN (%s) AND IS_NULL(city) = 0 '
                                  'AND (IS_NULL(country) = 0 OR IS_NULL(group_members) = 0 '
                                  'OR IS_NULL(group_events) = 0)' % event_ids_str})
            results = json.loads(results['json_encoded_response'])
            for i in range(len(results['column_1'])):
                event_info[results['column_1'][i]] = {
                    'city': results['column_2'][i],
                    'country': results['column_3'][i],
                    'group_members': results['column_4'][i],
                    'group_events': results['column_5'][i]
                }
            return event_info
        except UnicodeDecodeError:
            return {}

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
