import os
import re
import json
import base64
import asyncio
import logging

from .utils import generate_qr, remove_qr
from ..websockets.websocket import WhatsappWebsocket
from ..encryption.manager   import enc_manager
from ..messages import (
    init_message, reref, 
    MessageIdentifiers, restore_session,
    challenge_response, remember_me
)


class Client:
    """
    the client responsable to make
    a friendly "interface" with the user, the client need
    to take care of the authentication process and all of the messages
    that needed to be sended to the whatsapp websocket
    """
    _instance = None

    def __init__(self, id=None, loop=None):
        self.id   = id or str(base64.b64encode(os.urandom(16)), 'utf-8')
        self.name = None
        self.loop = loop or asyncio.get_event_loop()

        if Client._instance:
            raise Exception('a running instance of client already exists')
        Client._instance = self
    
    async def connect(self, token=None, server_token=None, mkey=None, remember_me=False):
        """
        start doing all the required things to connect to whatsapp
        and then starting the authentication process
        """
        self.token = token
        self.server_token = server_token

        self.wb = WhatsappWebsocket(self)
        await self.wb

        enc_manager._generate_keys(mkey=mkey)
        await self.start_authentication(remember_me)

    async def start_authentication(self, remember):
        """
        start authenticating with whatsapp backend, generating
        qr code and requesting re refrence when need
        """
        await self.wb.send(
            init_message(self.id)
        )

        if self.token and self.server_token:
            return (await self._login())

        time = re.compile(*MessageIdentifiers.TIME)
        s    = re.compile(*MessageIdentifiers.S_RANGE(1, 4))
        await self.wb.send(remember_me(remember))

        while (not self.token) or (not self.server_token):
            try:
                response = await asyncio.wait_for(
                    asyncio.shield(self.wb.recv), 15, loop=self.loop
                )
            except asyncio.TimeoutError:
                await self._request_reref()
                continue

            if isinstance(response, bytes): # nothing useful 4 this authtication
                continue

            tag, content = response.split(',', 1)
            as_python = json.loads(content)

            if time.match(tag):
                ref = as_python.get('ref', None)

                if ref:
                    generate_qr(
                        '{},{},{}'.format(
                            ref, str(enc_manager.public_b64, 'utf-8'), self.id
                        )
                    )
                continue
            
            if s.match(tag):
                type = as_python[0].lower()

                if type == 'conn':
                    await self._get_connection_info(as_python[1])
                    break
                raise ValueError('unexpected message, expected "conn" but recved %s' %type)
        remove_qr()

    async def _login(self):
        """
        TODO:
        always recving error 401 when phone is paired and a valid login
        data has been send
        """
        s = re.compile(*MessageIdentifiers.S_RANGE(1, 2))
        _error_messages = {
            401: 'phone is unpaired',
            403: 'access denied',
            405: 'already logged',
            409: 'logged in from another location',
            -1: 'unexpected messaged recved'
        }
        await self.wb.send(
            restore_session(self.token, self.server_token, self.id)
        )

        # first recv message cmd 
        # second message is the conn
        for _ in range(2):
            response     = await self.wb.recv
            tag, content = response.split(',', 1)
            content = json.loads(content)

            if s.match(tag):
                type = content[0].lower()

                if type == 'cmd':
                    await self._solve_challenge(content[1])
                    continue

                if type == 'conn':
                    return (await self._get_connection_info(content[1]))
                raise ValueError('unexpected message, expected "conn" or "cmd" but recved %s' %type)
            status  = content.get('status', 200)
            # if recved message isent starting the s (s1, s2, s3 etc...)
            # meaning its a status message
    
            if status in _error_messages.keys():
                raise ValueError(_error_messages[status])

    async def _solve_challenge(self, message):
        challenge = message['challenge']
        decoded   = base64.b64decode(challenge)

        hash    = enc_manager.sign(decoded)
        encoded = base64.b64encode(hash)

        await self.ws.send(
            challenge_response(
                str(encoded, encoding='utf-8'),
                self.server_token,
                self.token
            )
        )

    async def _request_reref(self):
        await self.wb.send(reref())

    async def _get_connection_info(self, data):
        self.server_token = data['serverToken']
        self.ref   = data['ref']
        self.token = data['clientToken']
        self.name  = data['pushname']

        await enc_manager._generate_final_keys(data['secret'])

    @property
    def login_credentials(self):
        """
        returns a dict that can be saved and used for login next time
        without scanning the QR code
        """
        return {
            'token': self.token,
            'server_token': self.server_token,
            'mkey': enc_manager.mac_key
        }

    @classmethod
    def get_running_instance(cls):
        return Client._instance

