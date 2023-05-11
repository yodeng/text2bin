#!/usr/bin/env python

import os
import sys
import argparse

from io import StringIO

from ._crypto import CryptoData


class Bopen(object):

    def __init__(self, name):
        self.name = os.path.abspath(name)
        self.chunksize = self.get_chunksize(name)
        self.data = self._cache_data()

    def _cache_data(self):
        try:
            dh = StringIO()
            c = b""
            for chunk in CryptoData.decrypt_file_iter(self.name, chunksize=self.chunksize):
                c += chunk
            dh.write(c.decode())
            del c
            dh.seek(0)
        except ValueError:
            dh = open(self.name)
        except Exception as err:
            raise err
        return dh

    def __enter__(self):
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        line = self.readline()
        if not line:
            raise StopIteration
        return line

    def __iter__(self):
        return self

    next = __next__

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

    def __del__(self):
        self.close()

    def seek0(self):
        self.data.seek(0)

    @staticmethod
    def get_chunksize(name):
        filesize = os.path.getsize(name)
        size = (filesize // 100) // 16 * 16
        return max(size, 64 * 1024)

    @staticmethod
    def tobin(infile, outbin):
        chunksize = Bopen.get_chunksize(infile)
        CryptoData.encrypt_file(infile, outbin, chunksize=chunksize)
