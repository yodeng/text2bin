#!/usr/bin/env python

import os
import re
import sys
import struct
import argparse
import subprocess

from functools import wraps
from io import StringIO, BytesIO
from os.path import join, realpath, abspath, exists, isfile, basename, dirname, split, expanduser

from shutil import which as _which

from ._crypto import CryptoData


class Bopen(object):

    def __init__(self, name, key=None, text=True, force_binary=False):
        self.name = abspath(name)
        self.key = key
        self.text = text
        self.chunksize = self.get_chunksize(name)
        self.force_binary = force_binary
        self.data = self._cache_data()

    def _cache_data(self):
        dh = self.text and StringIO() or BytesIO()
        try:
            c = b""
            for chunk in CryptoData.decrypt_file_iter(self.name, chunksize=self.chunksize, key=self.key):
                c += chunk
            c = c.decode() if self.text else c
            dh.write(c)
            del c
            dh.seek(0)
        except (ValueError, struct.error) as err:
            if self.force_binary:
                raise ValueError(f"can not open file {self.name}")
            dh = open(self.name, self.text and "r" or "rb")
        except Exception as err:
            raise err
        return dh

    def __enter__(self):
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __next__(self):
        line = self.readline()
        if line == "" or line == b"":
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
        if hasattr(self, "data") and not self.closed:
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

    @classmethod
    def tobin(cls, infile, outbin, key=""):
        chunksize = cls.get_chunksize(infile)
        CryptoData.encrypt_file(infile, outbin, chunksize=chunksize, key=key)

    encrypt_file = tobin

    @classmethod
    def decrypt_file(cls, infile, outfile, key=""):
        chunksize = cls.get_chunksize(infile)
        CryptoData.decrypt_file(infile, outfile, chunksize=chunksize, key=key)


def exception_hook(et, ev, eb):
    err = '\x1b[1;31m{0}: {1}\x1b[0m'.format(et.__name__, ev)
    print(err)


def suppress_exceptions(*exception, msg="", trace_exception=True):
    def outer_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sys.excepthook = trace_exception and sys.__excepthook__ or exception_hook
            try:
                res = func(*args, **kwargs)
            except exception as e:
                err = msg or str(e)
                if isinstance(e, SystemExit):
                    if e.code:
                        exc = SystemExit(err)
                    else:
                        exc = e
                elif isinstance(e, KeyboardInterrupt):
                    exc = KeyboardInterrupt(err)
                else:
                    exc = RuntimeError(err)
                exc.__cause__ = None
                raise exc
            else:
                return res
        return wrapper
    return outer_wrapper


def is_exe(file_path):
    return (
        exists(file_path)
        and os.access(file_path, os.X_OK)
        and isfile(realpath(file_path))
    )


def canonicalize(path):
    return abspath(expanduser(path))


def which(program):
    ex = dirname(sys.executable)
    found_path = None
    fpath, fname = split(program)
    if fpath:
        program = canonicalize(program)
        if is_exe(program):
            found_path = program
    else:
        if is_exe(join(ex, program)):
            return join(ex, program)
        found_path = _which(program)
    return found_path


# @suppress_exceptions(BaseException, msg="program exit", trace_exception=False)
def exec_scripts(scripts, *args, verbose=True, pipe=True, key=None, **default_options):
    # exec an encrypto *.pl, *py, *.sh, *.r scripts
    _input = None
    cmd = []
    if args and which(scripts) and basename(scripts) in ["perl", "python", "sh", "bash", "python3", "python2", "Rscript"]:
        cmd.append(which(scripts))
        scripts = realpath(args[0])
        args = args[1:]
    prog = "sh"
    scripts = realpath(scripts)
    if not isfile(scripts):
        raise OSError("'%s' not found" % scripts)
    if scripts.endswith(".py"):
        if not cmd:
            cmd.append(which("python"))
        prog = "py"
    elif scripts.endswith(".pl"):
        if not cmd:
            cmd.append(which("perl"))
        prog = "pl"
    elif scripts.lower().endswith(".r"):
        if not cmd:
            cmd.append(which("Rscript"))
        cmd.append("--vanilla")
        prog = "r"
    else:
        if not cmd:
            cmd.append(which("bash"))
        cmd.extend(["-eo", "pipefail"])
    if not pipe:
        cmd.append(scripts)
    else:
        with Bopen(scripts, key=key, text=False) as fi:
            _input = fi.read()
        if prog == "sh":
            cmd.extend(["-s", "--"])
        else:
            cmd.append("-")
    cmd.extend(args)
    # command line flag args: '--input abc' like '__input="abc"' in default_options
    for k, v in default_options.items():
        k = re.sub("^_+", lambda x: x.group().replace("_", "-"), k)
        if k not in args:
            cmd.extend([k, v])
    res = subprocess.run(cmd, input=_input, shell=False,
                         stdout=subprocess.PIPE, stderr=-2)
    res.check_returncode()
    sys.stdout.buffer.write(res.stdout)


def is_root():
    if "--root" in sys.argv:
        root = True
        sys.argv.remove("--root")
    else:
        root = False
    return root
