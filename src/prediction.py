import json
from datetime import datetime

import gpudb
import pandas
import pytz
from sklearn import metrics
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
    events_df.dropna(inplace=True)
    events_df['timezone'] = events_df.apply(lambda e: pytz.timezone(e['timezone']), axis=1)
    events_df['time_local'] = events_df.apply(lambda e: e['time_utc'].astimezone(e['timezone']), axis=1)
    events_df['day_of_week'] = events_df.apply(lambda e: e['time_local'].weekday(), axis=1)
    events_df['hour'] = events_df.apply(lambda e: e['time_local'].hour, axis=1)

    train_model(events_df)


def get_events_from_db(db, offset=0):
    """
    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    :param int offset: How many rows from the result should be skipped. Used for pagination
    :rtype dict
    """
    events_response = db.aggregate_group_by(
        table_name=config.EVENT_RSVP_TABLE_NAME,
        column_names=['city', 'event_id', 'event_timestamp', 'SUM(response) AS yes_responses', 'lat', 'lon'],
        limit=30000,
        offset=offset,
        encoding='json',
        options={
            'expression': 'IS_NULL(city) = 0 AND event_timestamp < NOW()',
            'having': 'COUNT(*) >= 10'
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
            'city': events['column_1'][i],
            'event_id': events['column_2'][i],
            'time_utc': datetime.fromtimestamp(events['column_3'][i] / 1000, tz=pytz.utc),
            'yes_responses': events['column_4'][i],
            'lat': events['column_5'][i],
            'lon': events['column_6'][i]
        })

    df = pandas.DataFrame(event_records)
    return df


def train_model(events):
    """
    :param pandas.DataFrame events: Data about events
    """
    y = events['yes_responses'].values
    X = events[['city', 'hour', 'day_of_week']].values
    one_hot_encoder = preprocessing.OneHotEncoder()
    X = one_hot_encoder.fit_transform(X, y)

    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.15, shuffle=True)
    cls = neural_network.multilayer_perceptron.MLPRegressor((200, 200, 200), max_iter=1000)
    cls.fit(X_train, y_train)
    y_pred = cls.predict(X_train)
    score = metrics.r2_score(y_train, y_pred)
    print(score)


if __name__ == '__main__':
    main()
