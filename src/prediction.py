import config
import gpudb
import pandas
import json


def main():
    db = gpudb.GPUdb(config.GPUDB_HOST, config.GPUDB_PORT)

    events_response = db.aggregate_group_by(
        table_name=config.EVENT_RSVP_TABLE_NAME,
        column_names=['city', 'event_id', 'event_timestamp', 'SUM(response) AS yes_responses'],
        limit=1000,
        offset=0,
        encoding='json',
        options={
            'expression': 'IS_NULL(city) = 0 AND event_timestamp < NOW()',
            'having': 'COUNT(*) >= 10'
        }
    )['json_encoded_response']

    event_response_json = json.loads(events_response)
    num_events = len(event_response_json['column_1'])

    event_records = []

    for i in range(num_events):
        event_records.append({
            'city': event_response_json['column_1'][i],
            'event_id': event_response_json['column_2'][i],
            'event_timestamp': event_response_json['column_3'][i],
            'yes_responses': event_response_json['column_4'][i]
        })

    df = pandas.DataFrame(event_records)
    print(df)


if __name__ == '__main__':
    main()
