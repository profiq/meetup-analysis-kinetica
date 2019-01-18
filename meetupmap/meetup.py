import collections
import functools
import json
import multiprocessing
import threading

import gpudb
import websocket

import apiutils
import config


def main():
    """
    Start listening to the Meetup.com RSVP stream (uses WebSockets).
    If a RSVP is received store it in the database.
    """
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    rsvp_queue = multiprocessing.Queue()
    event_info_provider = apiutils.EventInfoProvider(db)

    storer = threading.Thread(
        target=store_rsvps,
        kwargs={'db': db, 'queue': rsvp_queue, 'event_info_provider': event_info_provider})
    storer.start()

    websocket.enableTrace(False)
    on_message = functools.partial(add_to_storing_queue, queue=rsvp_queue)
    ws = websocket.WebSocketApp(config.MEETUP_API_RSVP_ENDPOINT, on_message=on_message)
    ws.run_forever()


def add_to_storing_queue(_, rsvp_json, queue):
    """
    Add RSVPs to a queue for storing. This solution is chosen because some additional info about
    the event is requested from the DB or Meetup API. This might take some time and we need to process other
    incoming RSVPs without waiting

    :param str rsvp_json: Raw message received from Meetup.com socket (JSON string)
    :param multiprocessing.Queue queue: Queue to put the RSVP in
    """
    rsvp = json.loads(rsvp_json)
    queue.put(rsvp)
    print('[stream] RSVP ID: %d in queue' % rsvp['rsvp_id'])


def store_rsvps(db, queue, event_info_provider):
    """
    Process and store RSVPs received from a queue. Runs in a separate thread.
    RSVPs are transformed to a form matching table structure and suitable for storing.

    After 10 RSVPs are collected, addional event info not present in the raw RSVP is received and then all 10
    records are stored. Meetup API limits number of requests to 30 per 10 seconds. Some endpoints allow us
    to receive information about multiple events at once. This allows us to reduce the number of requests required.

    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    :param multiprocessing.Queue queue: Queue providing RSVPs to store
    :param apiutils.EventInfoProvider event_info_provider: Provides additional event information not present in the RSVP
    """
    rsvp_record_bases = []

    while True:
        rsvp = queue.get()
        print('[store] RSVP ID: %d processing started' % rsvp['rsvp_id'])
        rsvp_record_base = record_base_from_rsvp(rsvp)
        rsvp_record_bases.append(rsvp_record_base)

        if len(rsvp_record_bases) == 10:
            event_ids = [r['event_id'] for r in rsvp_record_bases]
            event_info = event_info_provider.get_info(event_ids)
            rsvp_records = add_event_info_to_record_bases(event_info, rsvp_record_bases)
            save_records_to_db(db, rsvp_records)
            rsvp_record_bases = []


def record_base_from_rsvp(rsvp):
    """
    Transform raw RSVP received from Meetup API to a structure suitable for the DB.
    Result of this transformation does not contain all the required information, hence the name "record_base"

    :param dict rsvp: Raw RSVP received from Meetup.com API
    :rtype: collections.OrderedDict
    """
    rsvp_record = collections.OrderedDict()
    rsvp_record['event_id'] = rsvp['event']['event_id']
    rsvp_record['name'] = rsvp['event']['event_name']
    rsvp_record['url'] = rsvp['event']['event_url']
    rsvp_record['event_timestamp'] = rsvp['event']['time'] if 'time' in rsvp['event'] else None
    rsvp_record['lat'] = rsvp['venue']['lat'] if 'venue' in rsvp else None
    rsvp_record['lon'] = rsvp['venue']['lon'] if 'venue' in rsvp else None
    rsvp_record['rsvp_id'] = rsvp['rsvp_id']
    rsvp_record['response'] = 1 if rsvp['response'] == 'yes' else 0
    rsvp_record['rsvp_timestamp'] = rsvp['mtime']
    return rsvp_record


def add_event_info_to_record_bases(event_info, rsvp_record_bases):
    """
    Add additional event information received from EventInfoProvider to RSVP record bases

    :param dict event_info: Dictionary containing additional event info. Key is the event_id, value is a dict
    :param rsvp_record_bases: List of record bases to augment by additional event info
    :rtype: list
    """
    rsvp_records = []
    for rsvp_base in rsvp_record_bases:
        rsvp = rsvp_base.copy()
        if rsvp['event_id'] in event_info:
            rsvp.update(event_info[rsvp['event_id']])
        else:
            rsvp['city'] = rsvp['country'] = rsvp['group_members'] = rsvp['group_events'] = None
        rsvp_records.append(rsvp)
    return rsvp_records


def save_records_to_db(db, rsvp_records):
    """
    Save records to the database
    Notice the `ensure_ascii=False parameter`. It's required to correctly store unicode characters

    :param gpudb.GPUdb db: Connection to Kinetica's GPUdb
    :param list rsvp_records: Records to store
    :return:
    """
    for record in rsvp_records:
        dumped_record = json.dumps(record, ensure_ascii=False)
        response = db.insert_records(config.EVENT_RSVP_TABLE_NAME, dumped_record, list_encoding='json')

        if response['status_info']['status'] == 'OK':
            print('[store] Record %d inserted' % record['rsvp_id'])
        else:
            print('[store] Error while storing record %d' % record['rsvp_id'])
            print(response['status_info']['message'])


if __name__ == '__main__':
    main()

