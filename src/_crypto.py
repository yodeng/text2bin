#!/usr/bin/env python

import os
import sys
import json
import struct
import string
import base64
import random

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

__all__ = ["CryptoData"]


def real_key(key, seed=2050):
    random.seed(seed)
    abc = string.ascii_letters + string.punctuation + string.digits
    one_time_pad = list(abc)
    one_key = "".join(random.sample(abc, 32))
    random.shuffle(one_time_pad)
    ciphertext = ''
    for idx, char in enumerate(key):
        charIdx = abc.index(char)
        keyIdx = one_time_pad.index(one_key[idx])
        cipher = (keyIdx + charIdx) % len(one_time_pad)
        ciphertext += abc[cipher]
    return ciphertext


def add_to_16(v, salt="add_to_16"):
    s = v + salt
    while len(s) % 32 != 0:
        s += "\0"
    return base64.b64encode(s.encode())[:32].decode()


class CryptoData(object):

    qss = struct.calcsize("Q")

    @staticmethod
    def encrypt_data(data, key_loop=20, key=""):
        # base64.b64encode(os.urandom(24))
        key = key or "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        if isinstance(data, bytes):
            data = data.decode()
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = cipher.encrypt(pad(data.encode(), AES.block_size))
        data = iv + data
        return data

    @classmethod
    def encrypt_file(cls, in_file=None, out_file=None, chunksize=64*1024, key_loop=50, key=""):
        key = key or "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        iv = Random.new().read(AES.block_size)
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_file)
        pos = 0
        with open(in_file, "rb") as fi, open(out_file, "wb") as fo:
            fo.write(struct.pack('<Q', filesize))
            fo.write(iv)
            while pos < filesize:
                chunk = fi.read(chunksize)
                pos += len(chunk)
                if pos == filesize:
                    chunk = pad(chunk, AES.block_size)
                enc_data = cipher.encrypt(chunk)
                fo.write(enc_data)

    @classmethod
    def decrypt_data(cls, data, key_loop=20, key=""):
        key = key or "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        if not isinstance(data, bytes):
            raise TypeError("only bytes data allowed")
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        iv = data[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)
        return data

    @classmethod
    def decrypt_file_iter(cls, in_file, chunksize=64*1024, key_loop=50, key=""):
        key = key or "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        with open(in_file, 'rb') as fi:
            struct.unpack('<Q', fi.read(cls.qss))[0]
            iv = fi.read(AES.block_size)
            for i in range(key_loop):
                key = real_key(key)
            key = add_to_16(key).encode()
            cipher = AES.new(key, AES.MODE_CBC, iv)
            filesize = os.path.getsize(in_file)
            pos = cls.qss + AES.block_size  # the filesize and IV.
            while pos < filesize:
                chunk = fi.read(chunksize)
                pos += len(chunk)
                chunk = cipher.decrypt(chunk)
                if pos == filesize:
                    chunk = unpad(chunk, AES.block_size)
                yield chunk

    @classmethod
    def decrypt_file(cls, in_file, out_file, chunksize=64*1024, key=""):
        with open(out_file, "wb") as fo:
            for data in cls.decrypt_file_iter(in_file, chunksize=chunksize, key=key):
                fo.write(data)
