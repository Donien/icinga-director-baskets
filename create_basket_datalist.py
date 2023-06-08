#!/usr/bin/env python3


import os
import sys
import csv
import json
import argparse



# Globals
## Meta
__NAME__        = sys.argv[0]
__VERSION__     = '0.1.0'
__DESCRIPTION__ = '''
This program is meant to create an Icinga Director Configuration Basket
containing data lists. They are created from simple csv files.
'''
__EPILOG__      = '''
'''

## Program related
DATALISTS_PATHS = ['./src/datalists/']
DATALISTS_OWNER = 'admin'
DATALISTS_ROLES = None
DELIMITER       = ';'
QUOTECHAR       = '"'



def get_files(path):
    # Checks for all files within a given path and returns a list of their paths

    file_paths = list()

    if os.path.isfile(path):
        file_paths.append(path)

    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            for file in files:
                abs_path = os.path.abspath(os.path.join(root,file))
                file_paths.append(abs_path)

    return file_paths



def get_duplicates(file_paths):
    # Returns a list of all duplicate file names

    found_duplicates = dict()
    found_basenames  = list()

    mapping = {file: os.path.basename(file) for file in file_paths}

    for basename in mapping.values():
        if list(mapping.values()).count(basename) > 1:
            found_basenames.append(basename)

    for basename in found_basenames:
        basename_list = list()
        for key, value in mapping.items():
            if basename == value:
                basename_list.append(key)
        if basename_list:
            found_duplicates.update({basename: basename_list})

    return found_duplicates



def build_datalist(file):
    # Create a single datalist from a single csv file

    entries = []
    with open(file, 'r') as csv_file:
        rows = csv.reader(csv_file, delimiter=DELIMITER, quotechar=QUOTECHAR)
        for key, value in rows:
            key   = key.strip()
            value = value.strip()
            entries.append({
                              'entry_name': key,
                              'entry_value': value,
                              'format': 'string',
                              'allowed_roles': DATALISTS_ROLES,
                           })

    datalist_obj = {
                     os.path.basename(file): {
                       'entries': entries,
                       'list_name': os.path.basename(file),
                       'owner': DATALISTS_OWNER,
                     }
                   }

    return datalist_obj



def merge_datalists(datalists):
    # Returns an object containing all datalists

    outer_datalist = {
                       'DataList': {},
                     }

    for datalist in datalists:
        outer_datalist['DataList'].update(datalist)

    return outer_datalist



def to_json(obj):
    # Print dictionary object as json string

    json_string = json.dumps(obj)
    return json_string



def parse_cmdline():
    # Parse given command line arguments

    global DATALISTS_PATHS
    global DATALISTS_OWNER
    global DATALISTS_ROLES
    global DELIMITER
    global QUOTECHAR

    parser = argparse.ArgumentParser(
                                     prog=__NAME__,
                                     description=__DESCRIPTION__,
                                     epilog=__EPILOG__,
                                     add_help=False
                                    )

    parser.add_argument(
                        '-h',
                        '--help',
                        action='help',
                        default=argparse.SUPPRESS,
                        help='Shows this help message')

    parser.add_argument(
                        '-t',
                        '--target',
                        action='append',
                        dest='target',
                        default=None,
                        help='The path to either a directory or a specific file to source (can be specified multiple times)'
                       )

    parser.add_argument(
                        '-d',
                        '--delimiter',
                        action='store',
                        dest='delimiter',
                        default=DELIMITER,
                        help=f'The delimiter that should be used for the csv files (default: \'{DELIMITER}\')'
                       )

    parser.add_argument(
                        '-e',
                        '--enclosure',
                        action='store',
                        dest='quotechar',
                        default=QUOTECHAR,
                        help=f'The enclosure character that should be used for the csv files (default: \'{QUOTECHAR}\')'
                       )

    parser.add_argument(
                        '-o',
                        '--owner',
                        action='store',
                        dest='owner',
                        default=DATALISTS_OWNER,
                        help='The owner of the data lists'
                       )

    parser.add_argument(
                        '-r',
                        '--roles',
                        action='append',
                        dest='roles',
                        default=None,
                        help='The Icinga Web 2 roles the data lists should be available to'
                       )

    args = parser.parse_args()

    if args.target:
        DATALISTS_PATHS = list(set(args.target))

    if args.roles:
        DATALISTS_ROLES = list(set(args.roles))

    DATALISTS_OWNER = args.owner
    DELIMITER       = args.delimiter
    QUOTECHAR       = args.quotechar



def main():
    parse_cmdline()
    file_list = list()

    for path in DATALISTS_PATHS:
        file_list += get_files(path)

    if duplicates := get_duplicates(file_list):
        # WIP: write better error message
        print('Duplicate file names...')
        print(duplicates)
        sys.exit(1)

    datalists = [build_datalist(file) for file in file_list]

    merged = merge_datalists(datalists)
    print(to_json(merged))



if __name__ == '__main__':
    main()
