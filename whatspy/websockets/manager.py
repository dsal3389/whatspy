import asyncio
import collections
import functools
import queue
import json
import re

from .breader import ByteReader
from ..messages.message   import MessageIdentifiers
from ..encryption.manager import enc_manager


__all__ = ('manager',)


IGNORE_MESSAGES_WITH_TAG = [
    re.compile(*MessageIdentifiers.S_RANGE(1, 4)), # ignore s1 s2 s3 s4, those handled by the client authentication
    re.compile(*MessageIdentifiers.DUMMY)
]


class Manager:
    """
    all incoming data goes through the manager
    to keep track of the data and redirect it to the correct place
    """
    _messages_to_process = queue.SimpleQueue()
    # if the manager processing a message, the next message will go to
    # a FIFO query to be processd when the manager finish with the current message

    _lock = asyncio.Lock()

    def __init__(self):
        self._loop = asyncio.get_event_loop()

    async def handle_message(self, message):
        self._messages_to_process.put(message)
        self._loop.create_task(
            self._parse_next_message()
        )

    async def _parse_next_message(self):

        async with self._lock:
            # the lock will make it act like FIFO
            # first incoming message first to be finsihed processed
            # helping improve memroy, not spamming the memory and the CPU 
            # make processing messages faster because the loop handling 1 message at a time and not 10
            message = self._messages_to_process.get(block=False)

            if isinstance(message, bytes):
                return (await self._handle_bytes_message(message))
            return (await self._handle_string_message(message))

    async def _handle_string_message(self, message):
        try:
            tag, content = map(lambda n: n.strip(), message.split(',', 1))
        except ValueError: return 

        ignore = (mti.match(tag) for mti in IGNORE_MESSAGES_WITH_TAG)
        if ignore: return

        content = json.loads(content)
        if re.compile(*MessageIdentifiers.S).match(tag):
            tag, content = content
        
        status = content.get('status', 200)
        if status != 200:
            raise Exception('recved status %d' %status)
        
        #print("processing message...", message)

    async def _handle_bytes_message(self, message):
        if not enc_manager.ready: # sometimes a byte message is recved befor the keys are ready
            await enc_manager.wait_to_be_ready()

        tag, content = message.split(b',', 1)
        message_hash = content[:32] # first 32 byte is the message hash
        content = content[32:]

        checksum = await enc_manager.checksum(message_hash, content)
        if not checksum:
            raise ValueError('recved bytes message, hash mismatch')

        content = await enc_manager.dencrypt(content)
        breader = ByteReader(content)
        breader.read_node()


manager = Manager()
