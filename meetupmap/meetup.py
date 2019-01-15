import collections
import functools
import json

import gpudb
import websocket

from src import apiutils
from src import config
import multiprocessing
import threading


def main():
    """
    Start listening to the Meetup.com RSVP stream (uses WebSockets).
    If a RSVP is received store it in the database.
    """
    db = gpudb.GPUdb(host=config.GPUDB_HOST, port=config.GPUDB_PORT)
    rsvp_queue = multiprocessing.Queue()
    event_info_provider = apiutils.EventInfoProvider(db, True)

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
    Adds RSVPs to a queue for storing. This solution is chosen because some additional info about
    the event is requested from the DB or Meetup API. This might take some time and we need to process other
    incoming RSVPs without waiting

    :param str rsvp_json: Raw message received from Meetup.com socket (JSON string)
    :param multiprocessing.Queue queue: Queue to put the RSVP in
    """
    rsvp = json.loads(rsvp_json)
    queue.put(rsvp)
    print('[stream] RSVP ID: %d in queue' % rsvp['rsvp_id'])

    """
        response = db.insert_records('event_rsvp', json.dumps(rsvp_record, ensure_ascii=False), list_encoding='json')

        if response['status_info']['status'] == 'OK':
            print('[stream] RSVP ID: %d stored in DB' % rsvp['rsvp_id'])
        else:
            print('[stream] Error while storing')
            print(response)
    """


def store_rsvps(db, queue, event_info_provider):
    """
    :param gpudb.GPUdb db:
    :param multiprocessing.Queue queue:
    :param apiutils.EventInfoProvider event_info_provider:
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
            print(len(rsvp_records))
            save_records_to_db(db, rsvp_records)
            rsvp_record_bases = []


def record_base_from_rsvp(rsvp):
    """
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
    rsvp_records = []
    for rsvp_base in rsvp_record_bases:
        rsvp = rsvp_base.copy()
        if rsvp['event_id'] in event_info:
            rsvp.update(event_info[rsvp['event_id']])
        else:
            rsvp['city'] = rsvp['country'] = rsvp['group_members'] = rsvp['group_events'] = None
    return rsvp_records


def save_records_to_db(db, rsvp_records):
    dumped_records = [json.dumps(r, ensure_ascii=False) for r in rsvp_records]
    response = db.insert_records('event_rsvp', dumped_records, list_encoding='json')

    if response['status_info']['status'] == 'OK':
        print('[store] Inserted %d records' % response['count_inserted'])
    else:
        print('[store] Error while storing')
        print(response)


if __name__ == '__main__':
    while True:
        main()

