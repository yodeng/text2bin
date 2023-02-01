#!/usr/bin/env python

import os
import struct
import hashlib
import argparse


class Bread(object):

    def __init__(self, handler):
        self.handler = handler
        self.line = b""

    def __iter__(self):
        return self

    def __next__(self):
        line = self.line
        while True:
            b = self.handler.read(1)
            if not b_line:
                if line:
                    return line
                raise StopIteration
            line += b
            _ = self.handler.read(Bopen.iv)
            if b == b"\n":
                return line


class Bopen(object):

    qss = struct.calcsize("Q")
    iv = 1

    def __init__(self, name):
        self.name = name
        self.handler = open(self.name, "rb")
        offset = struct.unpack('<Q', self.handler.read(self.qss))[0]
        self.handler.read(offset-self.qss)

    @staticmethod
    def hnum(num):
        b1 = (num & 0x000000FF) << 24
        b2 = (num & 0x0000FF00) << 8
        b3 = (num & 0x00FF0000) >> 8
        b4 = (num & 0xFF000000) >> 24
        return sum((b1, b2, b3, b4))

    def __enter__(self):
        return self.iterlines()

    def close(self):
        if not self.closed:
            self.handler.close()

    @property
    def closed(self):
        return self.handler.closed

    def readlines(self):
        return list(self.iterlines())

    def iterlines(self):
        return Bread(self.handler)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @classmethod
    def tobin(cls, intext, outbin):
        with open(intext, "rb") as fi, open(outbin, "wb") as fo:
            size = cls.hnum(os.path.getsize(intext))
            md5 = hashlib.md5(str(size).encode()).hexdigest()[:2]
            offset = max(sum([ord(i) for i in md5]), 20)
            fo.write(struct.pack('<Q', offset))
            fo.write(os.urandom(offset-cls.qss))
            for line in fi:
                b_line = b""
                for c in line:
                    b_line += c.to_bytes(1, "big")
                    b_line += os.urandom(cls.iv)
                fo.write(b_line)
