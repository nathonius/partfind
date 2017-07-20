#!python3

import argparse
import logging
from os import walk
from os import path
import sqlite3

LOG = logging.getLogger(__name__)

def parse_partfile(part, c):
    pass

def build(args):
    pass

def search(args):
    # Search each root directory for partfiles
    partfiles = []
    for part in args.parts:
        LOG.info("Searching %s for PartFiles ...", part)
        for root, dirs, files in walk(part):
            LOG.info("\tIn %s", root)
            for f in files:
                if f.lower().endswith(".partfile.xml"):
                    LOG.info("\t\tFound PartFile %s", f)
                    partfiles.append(path.join(root, f))
        LOG.info("Done with %s.", part)
    print("Found {} PartFiles.".format(len(partfiles)))

    if len(partfiles) < 1:
        return False

    # Parse each PartFile
    conn = sqlite3.connect('partdb.db')
    c = conn.cursor()
    for part in partfiles:
        parse_partfile(part, c)
    conn.commit()
    conn.close()

def init_parser():
    # Create the parent parser
    parser = argparse.ArgumentParser(
        description="Build/Search BentleyBuild PartFile trees for individual files")
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    subparsers = parser.add_subparsers()

    # Create the build parser
    build_parser = subparsers.add_parser('build', help='build help', aliases=['b', 'create', 'c'])
    build_parser.set_defaults(func=build)
    build_parser.add_argument('parts', nargs='+',
                              help='top level directories to search for partfiles')

    # Create the search parser
    search_parser = subparsers.add_parser('search', help='search help', aliases=['s', 'find', 'f'])
    search_parser.set_defaults(func=search)
    search_parser.add_argument('filename', nargs=1, dest='fname',
                               help='find parts for this file')
    return parser

def main():
    parser = init_parser()
    args = parser.parse_args()
    if args.verbose:
        LOG.setLevel(logging.INFO)
    return args.func(args)

if __name__ == "__main__":
    return main()