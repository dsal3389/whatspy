import websockets
import asyncio
import json

from .manager import manager


JSON_INDEX = 0


def message_as_json(message):
    global JSON_INDEX
    tag, content = message

    if callable(tag):
        tag = tag()

    sendable_string = '{}.--{},{}'.format(
        tag, JSON_INDEX, json.dumps(content)
    )
    
    JSON_INDEX += 1
    return sendable_string


class WhatsappWebsocket(object):
    """
    this websocket only serves two things
    send data and recv data

    when he recv it or sending the data he sending it to the manager first

    the client is the one who is sending data so the client will interact with the websocket
    but the websocket wont interract with the client, the manager will 
    """
    def __init__(self, client, uri="wss://web.whatsapp.com/ws", origin="https://web.whatsapp.com"):
        self.uri = uri
        self.origin  = origin
        self._client = client
        self.loop = asyncio.get_event_loop()
        self.recv = self.loop.create_future()
        # the recv future is if someone want to listen for the icoming traffic 
        # without interrupting the "listen loop" 

    async def connect(self):
        """
        connecting to the whatsapp websocket and start listening for incoming data
        """
        self.socket = await websockets.connect(self.uri, origin=self.origin)
        self.loop.create_task(self.listen())

    async def listen(self):
        """
        where the listen loop is running, for listening for incoming traffic
        please use the .recv variable

        example:
            message = await client.recv

            or

            client.recv.add_done_callback(callback)

            to listen to all incoming traffic (not recommended)

            while True:
                message = await client.recv
                print(message)
        """
        while True:
            if self.recv.done():
                self.recv = self.loop.create_future()
            
            message = await self.socket.recv()
            await manager.handle_message(message)

            self.recv.set_result(message)

    async def send(self, message):
        if isinstance(message, bytes):
            await self.socket.send(message)
        assert isinstance(message, tuple), 'expected a tuple message if not bytes'

        m = message_as_json(message)
        await self.socket.send(m)

    def __await__(self):
        return self.connect().__await__()


