#!/usr/bin/env python3


import os
import sys
import csv
import json



# Globals
DATALISTS_PATH  = './src/datalists/'
DATALISTS_OWNER = 'admin'
DATALISTS_ROLES = None
DELIMETER       = ';'
QUOTECHAR       = '"'



def get_files(path):
    # Checks for all files within a given path and returns a list of their paths

    file_paths = list()

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
        rows = csv.reader(csv_file, delimiter=DELIMETER, quotechar=QUOTECHAR)
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
    json_string = json.dumps(obj)
    return json_string



def main():
    file_list = get_files(DATALISTS_PATH)

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
