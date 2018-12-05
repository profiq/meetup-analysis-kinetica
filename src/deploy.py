import gpudb

import config


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)

    gpudb.GPUdbTable(
        _type=config.EVENT_RSVP_TYPE,
        name=config.EVENT_RSVP_TABLE_NAME,
        options={'collection_name': config.EVENT_RSVP_COLLECTION},
        db=db)

    '''
    db.create_proc(
        proc_name=config.UDF_NAME,
        execution_mode=config.UDF_EXECUTION_MODE,
        files=config.UDF_FILES,
        command=config.UDF_COMMAND,
        args=config.UDF_FILES)
    '''

if __name__ == '__main__':
    main()
