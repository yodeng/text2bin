#!/usr/bin/env python

from .src import *
from ._version import __version__


def parseArg():
    parser = argparse.ArgumentParser(
        description="simple tools for convert text to bineary file and read bineary file",)
    parser.add_argument("-i", "--input", type=str,
                              help='input text file, required', required=True, metavar="<file>")
    parser.add_argument('-o', "--output", help="output bineary file, required",
                              type=str, required=True, metavar="<file>")
    parser.add_argument("-v", '--version',  action='version',
                        version="v" + __version__)
    return parser.parse_args()


def main():
    args = parseArg()
    Bopen.tobin(args.input, args.output)


if __name__ == "__main__":
    main()
