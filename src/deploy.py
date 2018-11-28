import gpudb

import config


def main():
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    db.create_proc(
        proc_name=config.UDF_NAME,
        execution_mode=config.UDF_EXECUTION_MODE,
        files=config.UDF_FILES,
        command=config.UDF_COMMAND,
        args=config.UDF_FILES)


if __name__ == '__main__':
    main()
