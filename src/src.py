#!/usr/bin/env python

import os
import sys
import argparse

from io import StringIO

from ._crypto import CryptoData


class Bopen(object):

    def __init__(self, name):
        self.name = name
        self.data = self._cache_data()

    def _cache_data(self):
        try:
            dh = StringIO()
            c = b""
            for chunk in CryptoData.decrypt_file_iter(self.name):
                c += chunk
            dh.write(c.decode())
            del c
            dh.seek(0)
        except:
            dh = open(self.name)
        return dh

    def __enter__(self):
        return self.data

    def read(self, n=None):
        return self.data.read(n)

    @property
    def closed(self):
        return self.data.closed

    def close(self):
        if not self.closed:
            self.data.close()

    def readlines(self):
        return self.data.readlines()

    def readline(self):
        return self.data.readline()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def seek0(self):
        self.data.seek(0)

    @classmethod
    def tobin(cls, intext, outbin):
        CryptoData.encrypt_file(intext, outbin)
