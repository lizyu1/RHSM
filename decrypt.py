#!/usr/bin/python

from Crypto.Cipher import AES
import base64

def decode(msg_text):
    secret_key = '1234567890123456'
    cipher = AES.new(secret_key,AES.MODE_ECB)
    decoded = cipher.decrypt(base64.b64decode(msg_text))
    return decoded.strip()
