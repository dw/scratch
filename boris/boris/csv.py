
from __future__ import absolute_import
import csv
import cStringIO

import twisted.application.service
import twisted.internet.defer


def write_csvs(pending_files):
    for path, lines in pending_files.iteritems():
        with open(path, 'a+') as fp:
            fp.write(chunk)
            fp.write('\n')


class CsvWriter(object):
    def __init__(self, service, name, header):
        self.service = service
        self.name = name
        self.header = header

    def write_row(self, row):
        if len(row) != len(self.header):
            raise TypeError('row must contain %d fields, got %d' %
                            (len(row), len(self.header))
        self.service.write_row(self.name, row)


class CsvService(twisted.application.service.Service):
    BYTES_MAX = 1048576
    WINDOW_SECS = 5.0 # 30.0 * 60.0

    def __init__(self, reactor):
        self.reactor = reactor
        self.pending_bytes = 0
        # name -> [list, of, rows]
        self.pending_files = {}
        # DelayedCall
        self.write_dc = None

        self._sio = cStringIO.StringIO()
        self._writer = csv.writer(self._sio, quoting=csv.QUOTE_ALL)

    def write_row(self, name, row):
