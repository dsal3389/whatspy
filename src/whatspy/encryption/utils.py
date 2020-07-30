import hmac
import hashlib

from math import ceil
from Crypto.Cipher import AES;
from Crypto.Hash import SHA256;


def hmac_sha256(key, data):
    return hmac.new(key, data, hashlib.sha256).digest()

def hkdf(length, key, info=b""): # https://en.wikipedia.org/wiki/HKDF
    salt = bytes([0] * 32)
    prk  = hmac_sha256(salt, key)
    t = b""
    okm = b""
    for i in range(ceil(length / 32)):
        t = hmac_sha256(prk, t + info + bytes([1 + i]))
        okm += t
    return okm[:length]

def AESUnpad(s):
    return s[:-ord(s[len(s)-1:])];

def AESDecrypt(key, ciphertext): # from whatsapp-web-reveng
    iv = ciphertext[:AES.block_size];
    cipher = AES.new(key, AES.MODE_CBC, iv);
    plaintext = cipher.decrypt(ciphertext[AES.block_size:]);
    return AESUnpad(plaintext);