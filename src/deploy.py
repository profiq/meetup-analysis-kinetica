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


if __name__ == '__main__':
    main()
