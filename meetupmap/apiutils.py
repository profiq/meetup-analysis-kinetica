import requests
import time
import json

import config


class EventInfoProvider:
    """
    Provide additional info about events:
     - city
     - country
     - group_members
     - group_event

    First searched RSVPs already present in the DB for the info and then uses Meetup API to get data about events
    not found in the database. Requests to Meetup API are limited to 30 per 10 seconds.
    """

    def __init__(self, db):
        """
        :param gpudb.GPUdb db: Connection to Kinetica DB
        """
        self._db = db
        self._table_name = config.EVENT_RSVP_TABLE_NAME

    def get_info(self, event_ids):
        """
        Get information about a list of events

        :param list event_ids: IDs of events info about which is requested
        :rtype: dict
        :returns: Dictionary with event IDs used as keys and dictionaries with event data as values
        """
        event_info = self._get_event_info_from_db(event_ids)
        print('[event] DB hits: %d' % len(event_info))
        event_ids_not_in_db = [e for e in event_ids if e not in event_info]
        event_info.update(self._get_info_from_meetup(event_ids_not_in_db))
        print('[event] Meetup hits: %d' % len(event_ids_not_in_db))
        return event_info

    def _get_info_from_meetup(self, event_ids):
        """
        Get event info from Meetup.

        EVENTS_ENDPOINT containing city, country and unique group urlname can be call once for all events
        Separate requests are required to get data about each group.

        :param list event_ids: IDs of events info about which is requested
        :rtype: dict
        """
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
        """
        Get event info from RSVPs already stored in the DB

        :param list event_ids: IDs of events info about which is requested
        :rtype: dict
        """
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
        """
        Get information about a group using Meetup.com API.
        Includes number of members and number of previous events

        :param urlname: unique urlname of the group
        :rtype: dict
        :return: Dictionary containing `group_members` and `group_events` keys
        """
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
        """
        Wrapper for requests.get().
        Waits for config.MEETUP_API_SLEEP_TIME to comply with Meetup API limits.
        Automatically adds API key to the request.

        :param str url: Request URL
        :param dict params: Dictionary containing GET parameters
        :rtype: tuple
        :returns: A tuple containing HTTP status code (int) and parsed JSON response (usually a dictionary)
        """
        params = {} if params is None else params
        params['key'] = config.MEETUP_API_KEY
        time.sleep(config.MEETUP_API_SLEEP_TIME)
        response = requests.get(url, params)
        return response.status_code, response.json()
