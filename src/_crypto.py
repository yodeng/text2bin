#!/usr/bin/env python

import os
import sys
import struct
import string
import base64
import random

from io import StringIO

from Crypto.Cipher import AES
from Crypto import Random

try:
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    from Crypto.Util.py3compat import bchr, bord

    def pad(data_to_pad, block_size):
        padding_len = block_size-len(data_to_pad) % block_size
        padding = bchr(padding_len)*padding_len
        return data_to_pad + padding

    def unpad(padded_data, block_size):
        pdata_len = len(padded_data)
        if pdata_len % block_size:
            raise ValueError("Input data is not padded")
        padding_len = bord(padded_data[-1])
        if padding_len < 1 or padding_len > min(block_size, pdata_len):
            raise ValueError("Padding is incorrect.")
        if padded_data[-padding_len:] != bchr(padding_len)*padding_len:
            raise ValueError("PKCS#7 padding is incorrect.")
        return padded_data[:-padding_len]


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

    @staticmethod
    def encrypt_string(data, key_loop=20):
        # base64.b64encode(os.urandom(24))
        key = "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        if isinstance(data, str):
            pass
        elif isinstance(data, dict):
            data = json.dumps(data)
        else:
            raise Exception("Only str or dict support")
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = cipher.encrypt(pad(data.encode(), AES.block_size))
        data = iv + data
        return base64.b64encode(data)

    @classmethod
    def encrypt_file(cls, in_file=None, out_filename=None, chunksize=64*1024, key_loop=50):
        key = "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        if not out_filename or not in_file:
            return
        infile = StringIO()
        with open(in_file, "rb") as fi:
            data = fi.read()
            enc_string = cls.encrypt_string(data.decode())
            infile.write(enc_string.decode())
        iv = os.urandom(16)
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        filesize = infile.tell()
        infile.seek(0)
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)
            pos = 0
            while pos < filesize:
                chunk = infile.read(chunksize).encode()
                pos += len(chunk)
                if pos == filesize:
                    chunk = pad(chunk, AES.block_size)
                outfile.write(encryptor.encrypt(chunk))
        infile.close()

    @classmethod
    def decrypt_string(cls, data, key_loop=20):
        '''
        data must be base64.b64encode()
        '''
        key = "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        for i in range(key_loop):
            key = real_key(key)
        key = add_to_16(key).encode()
        data = base64.b64decode(data)
        iv = data[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        data = unpad(cipher.decrypt(data[AES.block_size:]), AES.block_size)
        return data

    @classmethod
    def decrypt_file_iter(cls, in_filename, chunksize=64*1024, key_loop=50):
        key = "DFFa/1v5+RJMZnuqa5h5wdpvKoF9EEVy"
        with open(in_filename, 'rb') as infile:
            filesize = struct.unpack('<Q', infile.read(8))[0]
            iv = infile.read(16)
            for i in range(key_loop):
                key = real_key(key)
            key = add_to_16(key).encode()
            encryptor = AES.new(key, AES.MODE_CBC, iv)
            encrypted_filesize = os.path.getsize(in_filename)
            pos = 8 + 16  # the filesize and IV.
            while pos < encrypted_filesize:
                chunk = infile.read(chunksize)
                pos += len(chunk)
                chunk = encryptor.decrypt(chunk)
                if pos == encrypted_filesize:
                    chunk = unpad(chunk, AES.block_size)
                yield chunk

    @classmethod
    def decrypt_file(cls, in_filename, chunksize=64*1024):
        out = ""
        for line in cls.decrypt_file_iter(in_filename=in_filename, chunksize=chunksize):
            out += line.decode()
        return cls.decrypt_string(out).decode()
