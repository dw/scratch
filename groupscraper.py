#!/usr/bin/env python

import Queue
import urllib
import urllib2
import os
import threading
import re
import urlparse
import shelve

from datetime import datetime

import lxml.etree
import lxml.html

STOP_WORK = [None]
HAMMER = 5


print 'loading state'
state = shelve.open('state_groupscraper', protocol=2, writeback=True)
topic_urls = state.setdefault('topic_urls', set())
message_urls = state.setdefault('message_urls', set())
message_url_md5s = state.setdefault('message_url_md5s', {})
message_order = state.setdefault('message_order', [])
topics_todo = set()
newest = state.setdefault('newest', datetime(1549, 1, 1))

if not os.path.exists('messages'):
    os.makedirs('messages')

print 'done'


def parse_topiclist_date(s):
    now = datetime.utcnow()

    # 4:20am / 5:20pm
    try:
        dt = datetime.strptime(s, '%I:%M%p')
        return datetime(now.year, now.month, now.day)
    except ValueError:
        pass

    # May 21 
    try:
        dt = datetime.strptime(s, '%b %d')
        return datetime(now.year, dt.month, dt.day)
    except ValueError:
        pass

    # Oct 12 1983
    return datetime.strptime(s, '%b %d %Y')


def get_url(url):
    print 'getting', url
    req = urllib2.Request(url, None, headers={
        'User-agent': 'Daverson'
    })
    return urllib2.urlopen(req)


def get_url_html(url):
    return lxml.html.fromstring(get_url(url).read())


#print parse_topiclist_date('12:00pm')
#print parse_topiclist_date('May 21')
#print parse_topiclist_date('May 21 2011')
#raise


class Worker(object):
    def __init__(self, queue):
        self.queue = queue
        self._start()

    def _start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def do_one(self):
        done = False
        item = self.queue.get()
        if item is STOP_WORK:
            self.queue.task_done()
            return STOP_WORK

        try:
            self.do_work(item)
            done = True
        finally:
            if not done:
                self.queue.put(item)
            self.queue.task_done()

    def _run(self):
        while True:
            try:
                if self.do_one() is STOP_WORK:
                    print 'stopping'
                    return
            except:
                self._start()
                raise


class TopicListWorker(Worker):
    def __init__(self, queue, group):
        self.group = group
        Worker.__init__(self, queue)

    BASE = 'http://groups.google.com/'

    def do_work(self, start_idx):
        url = 'http://groups.google.com/group/%s/topics?gvc=2&start=%d' %\
            (self.group, start_idx)
        tree = get_url_html(url)

        trs = tree.cssselect('div.maincontoutboxatt table tr')
        for tr in trs:
            anchors = tr.cssselect('a')

            if not len(anchors):
                continue # header row

            for a in anchors:
                url2 = urlparse.urljoin(self.BASE, a.get('href'))
                if 'browse_thread' in url2:
                    break

            if 'browse_thread' not in url2:
                return

            if url2 not in topic_urls:
                topic_urls.add(url2)
                topics_todo.add(url2)


def get_group_info(group):
    url = 'http://groups.google.com/group/%s/topics?gvc=2' % group
    html = get_url_html(url)

    topics = None
    for span in html.cssselect('div.maincontboxhead span.uit'):
        s = span.text_content()
        if s.startswith('Topics'):
            topics = int(s.split()[-1])

    assert topics is not None
    return {
        'topics': topics
    }


group = 'mirah'
start = 0


def find_topics_todo(group, start, end):
    queue = Queue.Queue()
    for x in xrange(start, end, 30):
        queue.put(x)

    workers = [TopicListWorker(queue, group) for _ in xrange(HAMMER)]
    for _ in xrange(HAMMER):
        queue.put(STOP_WORK)

    queue.join()
    print 'Found', len(topics_todo), 'topics to scan'

info = get_group_info(group)
find_topics_todo(group, start, info['topics'])



fp = file('found', 'w', 1)

class MessageListWorker(Worker):
    def __init__(self, queue, group):
        self.group = group
        Worker.__init__(self, queue)

    BASE = 'http://groups.google.com/'

    def do_work(self, topic_url):
        next_url = topic_url
        urls = set()

        while next_url:
            html = get_url_html(next_url)
            next_url = None

            for a in html.cssselect('a'):
                if a.text_content() == 'Newer >':
                    next_url = urlparse.urljoin(self.BASE, a.get('href'))
                elif 'dmode=source' in a.get('href', ''):
                    urls.add(urlparse.urljoin(self.BASE,
                        a.get('href') + '&output=gplain'))

            for url in urls:
                print url
                fp.write('%s\n' % url)


def scan_message_lists():
    queue = Queue.Queue()
    for url in topic_urls:
        queue.put(url)

    workers = [MessageListWorker(queue, group) for _ in xrange(HAMMER)]
    for _ in xrange(HAMMER):
        queue.put(STOP_WORK)

    queue.join()
    print 'bang'

scan_message_lists()
