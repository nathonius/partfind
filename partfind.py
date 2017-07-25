#!python3

import argparse
import logging
from os import walk
from os import path
from lxml import etree
import sqlite3

LOG = logging.getLogger(__name__)
CONN = sqlite3.connect('partdb.db')
C = CONN.cursor()
MAKEFILES_READ = []
DEFAULT_TYPES = ('h', 'c', 'cpp', 'fdf')


def init_db():
    """Run db.sql if it hasn't already been run"""
    C.execute("SELECT sql FROM sqlite_master WHERE type='table'")
    if not C.fetchone():
        with open('db.sql', 'r') as fp:
            script = fp.read()
            C.executescript(script)
        C.commit()


def db_add_file(fpath, fname):
    """Add file to database, with given part as parent. Returns ID or False if it already exists."""
    # TODO: Check file doesn't already exist
    C.execute("INSERT INTO File (fpath, fname) VALUES (?, ?)", (fpath, fname))
    return C.lastrowid


def db_add_relation(parent, child):
    """Add a relation between a parent and child part"""
    pass
    return False


def db_add_part(partpath, partname):
    """Returns the ID of the newly added part, or False if part exists with same parent"""
    pass
    return False


def parse_tagfile(tags_path):
    """Read all files from a given tag file into the database"""
    with open(tags_path, 'r') as fp:
        LOG.info("Opened tag file %s", path.split(tags_path)[1])
        # skip first two lines
        for _ in range(2):
            next(fp)
        for line in fp:
            # we don't want to read the whole tag file, only the filenames
            if line.startswith("[Tags]"):
                break
            file_name, file_path = line.split(" ", maxsplit=1)
            db_add_file(file_path, file_name)
    C.commit()


def parse_partfile(partpath):
    root, part = path.split(partpath)
    partname = part.split(".PartFile.xml")[0]
    LOG.info("Parsing part %s", path.split(part))
    parent_id = db_add_part(partpath, partname)
    if parent_id:
        # Find subparts
        ptree = etree.parse(partpath)
        root = ptree.find('BuildContext')
        if not root:
            root = ptree.getroot()
        parts = root.findall('Part')
        # add / get each
        for p in parts:
            subparts = p.findall('SubPart')
            if p.get('Name') == partname:
                for s in subparts:
                    subpart_id = db_add_part(None, s.get('PartName'))
                    if subpart_id:
                        db_add_relation(parent_id, subpart_id)
            else:
                part_id = db_add_part(None, p.get('Name'))
                if part_id:
                    db_add_relation(parent_id, part_id)
                    for s in subparts:
                        subpart_id = db_add_part(None, s.get('PartName'))
                        if subpart_id:
                            db_add_relation(part_id, subpart_id)
            # Read PartFiles, looking for mke files
            if p.get('BMakeFile'):
                pass
                # parse_makefile(root, p.get('BMakeFile'), part_id)

        # parse mke files
    else:
        LOG.warn("WARNING: Part %s already in db", part)


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
    for part in partfiles:
        parse_partfile(part)
    CONN.commit()
    CONN.close()


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
    build_parser.add_argument('-t', '--types', nargs='*', default=DEFAULT_TYPES,
                              help='file types to include in the database')

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
    main()