#!/usr/bin/env python

from .src import *
from ._version import __version__


def parseArg():
    parser = argparse.ArgumentParser(
        description="tools for encrypt/decrypt a regular file",)
    parser.add_argument("-i", "--input", type=str, required=True,
                        help='input file, required', metavar="<file>")
    parser.add_argument("-k", "--key", type=str,
                        help='passwd for encrypt or decrypt', metavar="<str>")
    parser.add_argument("-o", "--output", type=str, required=True,
                        help="output file, required", metavar="<file>")
    parser.add_argument("-d", '--decrypt',  action='store_true', default=False,
                        help="decrypt file")
    parser.add_argument("-v", '--version',  action='version',
                        version="v" + __version__)
    return parser.parse_args()


# @suppress_exceptions(BaseException, msg="program exit", trace_exception=False)
def bincat():
    if len(sys.argv) == 1 or "-h" in sys.argv or "-help" in sys.argv or "--help" in sys.argv:
        sys.exit("Usage: \n\t%s enc_file [key]\n" % sys.argv[0])
    binfile = sys.argv[1]
    key = ""
    if len(sys.argv) > 2:
        key = sys.argv[2]
    if not os.path.isfile(binfile):
        raise IOError("No such file ", binfile)
    with Bopen(binfile, key=key, text=False) as fi:
        for line in fi:
            sys.stdout.buffer.write(line)


def main():
    args = parseArg()
    if not args.decrypt:
        Bopen.encrypt_file(args.input, args.output, key=args.key)
    else:
        Bopen.decrypt_file(args.input, args.output, key=args.key)
    os.chmod(args.output, os.stat(args.input).st_mode)


if __name__ == "__main__":
    main()
