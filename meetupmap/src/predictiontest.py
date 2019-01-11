import json
import os
import pickle
import time
from datetime import datetime

import gpudb
import pandas
import pytz
import requests
from sklearn import compose
from sklearn import model_selection
from sklearn import neural_network
from sklearn import preprocessing
from tzwhere import tzwhere

import config


def main():
    tzfinder = tzwhere.tzwhere()
    db = gpudb.GPUdb(config.GPUDB_HOST, config.GPUDB_PORT)
    events = get_events_from_db(db)
    events_df = events_to_dataframe(events)

    timezones = events_df.apply(lambda e: tzfinder.tzNameAt(e['lat'], e['lon']), axis=1)
    events_df['timezone'] = timezones
    event_info_provider = EventInfoProvider()
    events_df['event_info'] = events_df.apply(
        lambda e: event_info_provider.get_info_for_event(e['event_id']), axis=1)

    events_df.dropna(inplace=True)

    events_df['timezone'] = events_df.apply(lambda e: pytz.timezone(e['timezone']), axis=1)
    events_df['time_local'] = events_df.apply(lambda e: e['time_utc'].astimezone(e['timezone']), axis=1)
    events_df['day_of_week'] = events_df.apply(lambda e: e['time_local'].weekday(), axis=1)
    events_df['hour'] = events_df.apply(lambda e: e['time_local'].hour, axis=1)
    events_df['group_members'] = events_df.apply(lambda e: e['event_info']['group_members'], axis=1)
    events_df['past_events'] = events_df.apply(lambda e: e['event_info']['group_past_event_count'], axis=1)
    events_df['country'] = events_df.apply(lambda e: e['event_info']['country'], axis=1)

    events_df.dropna(inplace=True)

    train_model(events_df)


def get_events_from_db(db, offset=0):
    """
    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    :param int offset: How many rows from the result should be skipped. Used for pagination
    :rtype dict
    """
    events_response = db.aggregate_group_by(
        table_name=config.EVENT_RSVP_TABLE_NAME,
        column_names=['SUM(response) AS yes_responses', 'city', 'event_id', 'event_timestamp', 'lat', 'lon'],
        limit=3500,
        offset=offset,
        encoding='json',
        options={
            'expression': 'IS_NULL(city) = 0 AND event_timestamp < NOW()',
            'having': 'COUNT(*) >= 10',
            'sort_order': 'descending'
        })
    events_response_dict = json.loads(events_response['json_encoded_response'])
    return events_response_dict


def events_to_dataframe(events):
    """
    :param dict events:
    :rtype: pandas.DataFrame
    """
    event_records = []
    num_events = len(events['column_1'])

    for i in range(num_events):
        event_records.append({
            'city': events['column_2'][i],
            'event_id': events['column_3'][i],
            'time_utc': datetime.fromtimestamp(events['column_4'][i] / 1000, tz=pytz.utc),
            'yes_responses': events['column_1'][i],
            'lat': events['column_5'][i],
            'lon': events['column_6'][i]
        })

    df = pandas.DataFrame(event_records)
    return df


def train_model(events):
    """
    :param pandas.DataFrame events: Data about events
    """
    column_transformer = compose.ColumnTransformer([
        ('oh', preprocessing.OneHotEncoder(), ['city', 'hour', 'day_of_week', 'country']),
        ('do_nothing', preprocessing.MinMaxScaler(), ['group_members', 'past_events'])
    ])

    X = column_transformer.fit_transform(events)
    y = events['yes_responses'].values

    print(X.shape)
    cv = model_selection.ShuffleSplit(n_splits=5, test_size=0.1)
    cls = neural_network.multilayer_perceptron.MLPRegressor((250, 200), max_iter=3000)
    scores = model_selection.cross_val_score(cls, X, y, cv=cv)
    print(scores)
    print(scores.mean())
    print(scores.std())


class EventInfoProvider:

    def __init__(self):
        self._cache = self._init_cache()

    def get_info_for_event(self, event_id):
        """
        :param str event_id: ID of the event you want to know more about
        :rtype: dict
        """
        if event_id not in self._cache:
            time.sleep(0.35)
            params = {'event_id': event_id}
            response = requests.get('https://api.meetup.com/2/events', params=params).json()

            if len(response['results']) > 0:
                group_urlname = response['results'][0]['group']['urlname']
                time.sleep(0.35)
                response_group = requests.get('https://api.meetup.com/%s' % group_urlname,
                                              params={'fields': 'past_event_count'}).json()
                self._cache[event_id] = {
                    'country': response['results'][0]['venue']['country'].lower() if 'venue' in response['results'][
                        0] else None,
                    'group_members': response_group['members'] if 'members' in response_group else 0,
                    'group_past_event_count': response_group[
                        'past_event_count'] if 'past_event_count' in response_group else 0
                }
            else:
                self._cache[event_id] = None
            self.save_cache()
        return self._cache[event_id]

    def save_cache(self):
        with open('event_info_cache.pickle', 'wb') as dest:
            pickle.dump(self._cache, dest)

    @staticmethod
    def _init_cache():
        if os.path.exists('event_info_cache.pickle'):
            with open('event_info_cache.pickle', 'rb') as src:
                cache = pickle.load(src)
                print(len(cache))
        else:
            cache = {}
        return cache


if __name__ == '__main__':
    main()
