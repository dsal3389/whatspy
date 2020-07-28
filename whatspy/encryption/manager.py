import curve25519
import hashlib
import base64

from .utils import *


__all__ = ('enc_manager',)


class EncManager:

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

    def _is_final_valid(self):
        v = hmac_sha256(self.shared_secret_expended[32:64], self.secret[:32] + self.secret[64:])
        return v == self.secret[32:64]
    
    def _generate_keys(self):
        self.private = curve25519.Private()
        self.public  = self.private.get_public()

    @property
    def public_b64(self):
        return base64.b64encode(self.public.serialize())


enc_manager = EncManager()
