
import lxml.html
import datetime
import sqlite3

db = sqlite3.connect('main.db')
db.row_factory = sqlite3.Row

for row in db.execute('SELECT * FROM Messages ORDER BY timestamp'):
    dt = datetime.datetime.fromtimestamp(row['timestamp'])
    msg = [dt.strftime('%Y-%m-%d %H:%M:%S')]
    msg += [row['chatname']]

    if row['type'] in (10, 53, 100):
        continue
    if row['leavereason']:
        msg += ['* %s parted' % (row['author'],)]
    else:
        msg += ['%s<%s>' % ('*' if row['edited_by'] else '', row['author'],)]
        msg += [lxml.html.fromstring(row['body_xml']).text_content()]
    print ' '.join(msg).encode('utf-8')


