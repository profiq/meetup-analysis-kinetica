import gpudb
import config


def main():
    """
    Prepares database for storing Meetup.com RSVPs by creating all required tables.
    """
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    create_event_rsvp_table(db)
    add_city_column(db)
    add_prediction_columns(db)


def create_event_rsvp_table(db):
    """
    Creates an empty table for storing RSVPs from Meetup.com streaming API.
    Nothing happens if the table already exists

    :param gpudb.GPUdb db: Connection to Kinetica DB
    """
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


def add_city_column(db):
    """
    Add `city` column to the `event_rsvp` table. This column was added later
    so we need to ensure that it is present in older instances.

    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    """
    add_db_column(db, config.EVENT_RSVP_TABLE_NAME, 'city', 'string', 'char64,nullable,text_search')


def add_prediction_columns(db):
    """
    Add columns for additional data required for predicting number of `yes` responses for an event
    We didn't know in advance what data we need so these colums were added later. New data include the country where
    the event is taking place, number of Meetup group members, and number of previous events organized by the group

    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    """
    add_db_column(db, config.EVENT_RSVP_TABLE_NAME, 'country', 'string', 'char4,nullable')
    add_db_column(db, config.EVENT_RSVP_TABLE_NAME, 'group_members', 'long', 'nullable')
    add_db_column(db, config.EVENT_RSVP_TABLE_NAME, 'group_events', 'int', 'nullable')


def add_db_column(db, table, col_name, col_type, col_properties=''):
    """
    Add new column to a database table

    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    :param str table: Name of the database table which the new column will be added to
    :param str col_name: Name of the new column
    :param str col_type: Data type of the new column
    :param str col_properties: Additional properties assigned to the column
    """
    response = db.alter_table(
        table_name=table, action='add_column', value=col_name,
        options={'column_type': col_type, 'column_properties': col_properties})
    status_info = response['status_info']
    already_exists = 'message' in status_info and 'Duplicate attribute' in status_info['message']

    if already_exists:
        print('Column %s already exists' % col_name)
    elif status_info['status'] == 'ERROR':
        raise Exception(status_info['message'])
    else:
        print('Column %s successfuly created' % col_name)


if __name__ == '__main__':
    main()
