import asyncio
import json

import websockets

MEETUP_API_ENDPOINT = 'ws://stream.meetup.com/2/rsvps'


async def get_meetup_event(queue: asyncio.Queue):
    async with websockets.connect(MEETUP_API_ENDPOINT) as meetup_ws:
        while True:
            meetup_event_string = await meetup_ws.recv()
            meetup_event = json.loads(meetup_event_string)
            await queue.put(meetup_event)
            print('RSVP ID: %d in queue ready to be processed' % meetup_event['rsvp_id'])


async def save_meetup_event(queue: asyncio.Queue):
    while True:
        meetup_event = await queue.get()
        rsvp = {
            'rsvp_id': meetup_event['rsvp_id'],
            'response': meetup_event['response'] == 'yes',
            'timestamp': meetup_event['mtime'] * 1000,
            'event_id': meetup_event['event']['event_id']
        }
        queue.task_done()
        print('RSVP ID: %d stored in DB' % meetup_event['rsvp_id'])


async def main():
    meetup_event_queue = asyncio.Queue()
    saver = asyncio.create_task(save_meetup_event(meetup_event_queue))
    getter = asyncio.create_task(get_meetup_event(meetup_event_queue))
    await saver, getter

if __name__ == '__main__':
    asyncio.run(main())
