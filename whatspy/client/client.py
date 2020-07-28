import os
import re
import json
import base64
import asyncio
import logging

from .utils import generate_qr
from ..messages import init_message, reref, MessageIdentifiers
from ..websockets.websocket import WhatsappWebsocket
from ..encryption.manager   import enc_manager


class Client:
    _instance = None

    def __init__(self, loop=None):
        self.id   = str(base64.b64encode(os.urandom(16)), 'utf-8')
        self.name = 'unknown'
        self.loop = loop or asyncio.get_event_loop()

        if Client._instance:
            raise Exception('a running instance of client already exists')
        Client._instance = self
    
    async def connect(self, token=None, server_token=None):
        """
        start doing all the required things to connect to whatsapp
        and then starting the authentication process
        """
        self.token = token
        self.server_token = server_token

        self.wb = WhatsappWebsocket(self)
        await self.wb

        enc_manager._generate_keys()
        await self.start_authentication()

    async def start_authentication(self):
        """
        start authenticating with whatsapp backend, generating
        qr code and requesting re refrence when need
        """
        tag, content = init_message(self.id)
        await self.wb.send((tag, content))

        if self.token and self.server_token:
            # need to be implemented
            return

        time = re.compile(*MessageIdentifiers.TIME)
        s = re.compile(*MessageIdentifiers.S)

        while (not self.token) or (not self.server_token):
            try:
                response = await asyncio.wait_for(
                    asyncio.shield(self.wb.recv), 15, loop=self.loop
                )
            except asyncio.TimeoutError:
                await self._request_reref()
                continue

            if isinstance(response, bytes): # nothing useful 4 now
                continue

            tag, content = response.split(',', 1)
            as_python = json.loads(content)

            if time.match(tag):
                generate_qr(
                    '{},{},{}'.format(
                        as_python['ref'], str(enc_manager.public_b64, 'utf-8'), self.id
                    )
                )
                continue
            
            if s.match(tag):
                type = as_python[0].lower()
                if type == 'conn':
                    await self._get_connection_info(as_python[1])

    async def _request_reref(self):
        await self.wb.send(reref())

    async def _get_connection_info(self, data):
        self.server_token = data['serverToken']
        self.ref   = data['ref']
        self.token = data['clientToken']
        self.name  = data['pushname']

        await enc_manager._generate_final_keys(data['secret'])

    @classmethod
    def get_running_instance(cls):
        return Client._instance

