#!/usr/bin/env python

#
# Read Django test_data.json, check for duplicate items, dumping them to stdout
# if any are found. If none are found, reprint the entire file sorted by (kind,
# pk), sorting any list values, and with trailing whitespace stripped from the
# JSON output.
#

import json
import pprint
import sys

lst = json.load(sys.stdin)
key = lambda o: (o['model'], o['pk'])

unique = set()
bad = 0
for elem in lst:
    if key(elem) in unique:
        print 'duplicate pk!'
        print '----------'
        pprint.pprint(elem)
        print '----------'
        bad += 1
    unique.add(key(elem))

    # Sort lists of ForeignKey IDs for better diffing.
    for val in elem.itervalues():
        if isinstance(val, list):
            val.sort()

if bad:
    exit()

lst.sort(key=key)
s = json.dumps(lst, indent=4, sort_keys=True)
for line in s.splitlines():
    print line.rstrip()
