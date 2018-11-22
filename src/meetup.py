import asyncio
import json

import gpudb
import websockets
import collections

MEETUP_API_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'
GPUDB_HOST = '127.0.0.1'
GPUDB_PORT = '10004'  # Must be a string, otherwise does not work


async def get_meetup_event(queue: asyncio.Queue):
    async with websockets.connect(MEETUP_API_ENDPOINT) as meetup_ws:
        while True:
            meetup_event_string = await meetup_ws.recv()
            meetup_event = json.loads(meetup_event_string)
            await queue.put(meetup_event)
            print('RSVP ID: %d in queue ready to be processed' % meetup_event['rsvp_id'])


async def save_meetup_event(queue: asyncio.Queue, db: gpudb.GPUdb):
    while True:
        meetup_event = await queue.get()

        event = {
            'event_id': meetup_event['event']['event_id'],
            'name': meetup_event['event']['event_name'],
            'url': meetup_event['event']['event_url'],
            'timestamp': meetup_event['event']['time'],
            'lat': meetup_event['venue']['lat'] if 'venue' in meetup_event else None,
            'lng': meetup_event['venue']['lon'] if 'venue' in meetup_event else None
        }

        print(json.dumps(event))

        rsvp = {
            'rsvp_id': meetup_event['rsvp_id'],
            'response': 1 if meetup_event['response'] == 'yes' else 0,
            'timestamp': meetup_event['mtime'],
            'event_id': meetup_event['event']['event_id']
        }

        response_rsvp = db.insert_records('rsvp', json.dumps(rsvp), list_encoding='json')
        response_event = db.insert_records('event', json.dumps(event), list_encoding='json')

        print(response_event['status_info'])

        if response_rsvp['status_info']['status'] == 'OK':
            print('RSVP ID: %d stored in DB' % meetup_event['rsvp_id'])
        else:
            print('Error while storing: %s' % response_rsvp['status_info']['message'])

        queue.task_done()


async def main():
    db = gpudb.GPUdb(host='127.0.0.1', port='10004')
    meetup_event_queue = asyncio.Queue()
    saver = asyncio.create_task(save_meetup_event(meetup_event_queue, db))
    getter = asyncio.create_task(get_meetup_event(meetup_event_queue))
    await saver, getter


if __name__ == '__main__':
    asyncio.run(main())
