import gpudb

import config


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)

    try:
        gpudb.GPUdbTable(
            _type=config.EVENT_RSVP_TYPE,
            name=config.EVENT_RSVP_TABLE_NAME,
            options={'collection_name': config.EVENT_RSVP_COLLECTION},
            db=db)
    except gpudb.GPUdbException as e:
        if "Table '%s' exists;" % config.EVENT_RSVP_TABLE_NAME in str(e):
            print('Table for Meetup events already exists')
        else:
            raise e

    add_city_column(db)


def add_city_column(db: gpudb.GPUdb):
    response = db.alter_table(
        table_name=config.EVENT_RSVP_TABLE_NAME,
        action='add_column',
        value='city',
        options={'column_type': 'string', 'column_properties': 'char64,nullable,text_search'})

    status_info = response['status_info']

    already_exists = 'message' in status_info and 'Duplicate attribute' in status_info['message']

    if already_exists:
        print('Column already exists, but that is OK')
    elif status_info['status'] == 'ERROR':
        raise Exception(status_info['message'])


if __name__ == '__main__':
    main()
