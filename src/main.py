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


def bincat():
    root = is_root()

    def _cat(binfile, key="", text=False):
        with Bopen(binfile, key=key, text=text) as fi:
            for line in fi:
                sys.stdout.buffer.write(line)
    if len(sys.argv) == 1 or "-h" in sys.argv or "-help" in sys.argv or "--help" in sys.argv:
        sys.exit("Usage: \n\t%s enc_file [key]\n" % sys.argv[0])
    binfile = sys.argv[1]
    key = ""
    if len(sys.argv) > 2:
        key = sys.argv[2]
    if not os.path.isfile(binfile):
        raise IOError("No such file ", binfile)
    if root:
        func = _cat
    else:
        func = suppress_exceptions(
            BaseException, msg="program exit", trace_exception=False)(_cat)
    func(binfile, key=key, text=False)


def binrun():
    root = is_root()
    parser = argparse.ArgumentParser(
        description="tools for run a encrypt '.pl/.py/.sh/.r' scripts",
        add_help=False)
    parser.add_argument("--key", type=str,
                        help='passwd for decrypt', metavar="<str>")
    parser.add_argument("cmd", type=str,
                        help='run command, required', metavar="<command>")
    parser.add_argument("-v", '--version',  action='version',
                        version="v" + __version__)
    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "-help", "--help"]:
        parser.print_help()
        parser.exit()
    args, options = parser.parse_known_args()
    if root:
        func = exec_scripts
    else:
        func = suppress_exceptions(
            BaseException, msg="program exit", trace_exception=False)(exec_scripts)
    func(args.cmd, *options, key=args.key)


def main():
    args = parseArg()
    if not args.decrypt:
        Bopen.encrypt_file(args.input, args.output, key=args.key)
    else:
        Bopen.decrypt_file(args.input, args.output, key=args.key)
    os.chmod(args.output, os.stat(args.input).st_mode)


if __name__ == "__main__":
    main()
