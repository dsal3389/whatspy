import asyncio
import collections
import functools
import queue
import json

from ..encryption.manager import enc_manager


__all__ = ('manager',)


class Manager:
    """
    all incoming data goes through the manager
    to keep track of the data and redirect it to the correct place
    """
    # _requests_messages_queue  = collections.OrderedDict() # client requests
    # _responses_messages_queue = collections.OrderedDict() # websocket responses

    _messages_to_process = queue.SimpleQueue()
    # if the manager processing a message, the next message will go to
    # a FIFO query to be processd when the manager finish with the current message

    _lock = asyncio.Lock()

    def __init__(self):
        self._loop = asyncio.get_event_loop()

    async def handle_message(self, message):
        self._messages_to_process.put(message)
        self._loop.create_task(
            self._parse_message(self._messages_to_process.get(block=False))
        )

    async def _parse_message(self, message):
        async with self._lock: 
            # the lock will make it act like FIFO
            # first incoming message first to be finsihed processed
            # helping improve memroy, not spamming the memory and the CPU 
            # make processing messages faster because the loop handling 1 message at a time and not 10

            if isinstance(message, bytes):
                # need to implement
                return

            tag, content = map(lambda n: n.strip(), message.split(',', 1))
            content = json.loads(content)

            print("processing message...", message)


manager = Manager()
