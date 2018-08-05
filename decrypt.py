#!/usr/bin/python
"""
input a string and output the decryption of the string
"""
import base64
from crypto.Cipher import AES

def decode(msg_text):
    """
    input a string and output the decryption of the string
    """
    secret_key = '1234567890123456'
    cipher = AES.new(secret_key, AES.MODE_ECB)
    decoded = cipher.decrypt(base64.b64decode(msg_text))
    return decoded.strip()
