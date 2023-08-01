#!/usr/bin/env python

from .src import *
from ._version import __version__


def parseArg():
    parser = argparse.ArgumentParser(
        description="tools for encrypt a text file",)
    parser.add_argument("-i", "--input", type=str,
                              help='input text file, required', required=True, metavar="<file>")
    parser.add_argument("-k", "--key", type=str,
                              help='key passwd for encrypt', metavar="<str>")
    parser.add_argument('-o', "--output", help="output encrypted binary file, required",
                              type=str, required=True, metavar="<file>")
    parser.add_argument("-v", '--version',  action='version',
                        version="v" + __version__)
    return parser.parse_args()


def read_bin():
    binfile = sys.argv[1]
    key = ""
    if len(sys.argv) > 2:
        key = sys.argv[2]
    if not os.path.isfile(binfile):
        raise IOError("No such file ", binfile)
    with Bopen(binfile, key=key) as fi:
        for line in fi:
            sys.stdout.write(line)


def main():
    args = parseArg()
    Bopen.tobin(args.input, args.output, key=args.key)


if __name__ == "__main__":
    main()
