import curve25519
import hashlib
import asyncio
import base64

from .utils import *


__all__ = ('enc_manager',)


class EncManager:
    def __init__(self):
        self._ready = asyncio.Event()
        self.mac_key = None

    async def dencrypt(self, bytes):
        return AESDecrypt(self.enc_key, bytes)

    async def checksum(self, hash, bytes):
        return hmac_sha256(self.mac_key, bytes) == hash

    async def _generate_final_keys(self, secret):
        self.secret = base64.b64decode(secret)
        self.shared_secret = self.private.get_shared_key(
            curve25519.Public(self.secret[:32]), lambda a: a
        )
        self.shared_secret_expended = hkdf(80, self.shared_secret)
        
        if not self._is_final_valid():
            raise ValueError('hmac final keys mismatch')

        enc_key  = self.shared_secret_expended[64:] + self.secret[64:]
        denc_key = AESDecrypt(
            self.shared_secret_expended[:32], 
            enc_key
        )

        self.enc_key = denc_key[:32]
        self.mac_key = denc_key[32:64]
        self._ready.set()

    async def wait_to_be_ready(self):
        return (await self._ready.wait())

    def sign(self, data): # used for challenge
        return hmac_sha256(self.mac_key, data)

    def _is_final_valid(self):
        v = hmac_sha256(self.shared_secret_expended[32:64], self.secret[:32] + self.secret[64:])
        return v == self.secret[32:64]
    
    def _generate_keys(self, mkey):
        """
        start to generate authentication keys, and allowing to set the
        mac_key value in case exists
        """
        self.private = curve25519.Private()
        self.public  = self.private.get_public()
        self.mac_key = mkey

    @property
    def ready(self):
        return self._ready.is_set()

    @property
    def public_b64(self):
        return base64.b64encode(self.public.serialize())


enc_manager = EncManager()
