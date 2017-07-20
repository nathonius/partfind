#!python3

import argparse

def build():
    pass

def search():
    pass

def init_parser():
    # Create the parent parser
    parser = argparse.ArgumentParser(
        description="Build/Search BentleyBuild PartFile trees for individual files")
    parser.add_argument('-v', '--verbose', action='store_true')
    subparsers = parser.add_subparsers()

    # Create the build parser
    build_parser = subparsers.add_parser('build', help='build help', aliases=['b', 'create', 'c'])
    build_parser.set_defaults(func=build)
    build_parser.add_argument('strategies', nargs='+', dest='strats',
                              help='the build strategies to add to the database')

    # Create the search parser
    search_parser = subparsers.add_parser('search', help='search help', aliases=['s', 'find', 'f'])
    search_parser.set_defaults(func=search)
    search_parser.add_argument('filename', nargs=1, dest='fname',
                               help='find parts for this file')
    return parser

def main():
    pass

if __name__ == "__main__":
    main()