#!/usr/bin/env python2.5

"""
Absolutely minimalist implementation filesystem full text indexer in 62 lines of Python.

 * Script is 1894 bytes.
 * Runs from memory.
 * Blisteringly fast (for Python anyway). Indexes around 3.8mb/sec on a Macbook.
 * Incredibly naive (it'll try to index JPEGs)
 * Fun!

Usage:

`$ fts.py [your_source_dir]`

`Query? include stdio`

`0.00 your_source_dir/main.h`

*Looking for a real full text indexer for Python?* [http://whoosh.ca/ Check out Whoosh] 

Ghetto full text search: the world's smallest full text indexer.
"""
import array, math, operator, os, pprint, string, sys

terms, freqs = {}, array.array('L')
docs, docfreq, postings = [], [], []

trans = ''.join(map(chr, [c if chr(c) in (string.letters+string.digits) else 32
                            for c in range(256) ]))
def tokenize(s):
    return s.translate(trans).lower().split()

def term_id(t):
    tid = terms.get(t, None)
    if tid is None:
        tid = terms[t] = len(terms)
        postings.append(array.array('L'))
        freqs.append(0)
    return tid

def doc_id(fn):
    docs.append(fn)
    docfreq.append({})
    return len(docs) - 1

def index(fn):
    doc_terms = {}
    for token in tokenize(file(fn).read()):
        tid = term_id(token)
        doc_terms[tid] = doc_terms.get(tid, 0) + 1

    did = doc_id(fn)
    for tid, freq in doc_terms.iteritems():
        postings[tid].append(did)
        freqs[tid] += freq
        docfreq[did][tid] = freq

def index_dir(dir):
    for path, _, filenames in os.walk(dir):
        for fn in filenames: index(os.path.join(path, fn))

def score(did, qtids):
    tfs = [float(docfreq[did][tid]) / freqs[tid] for tid in qtids if tid > None]
    idfs = [math.log(float(len(docs)) / freqs[tid]) for tid in qtids]
    return sum(tf*idf for tf,idf in zip(tfs, idfs))

def intersect(its):
    last = [it.next() for it in its]
    indices = range(len(its))

    while True:
        if all(l == last[0] for l in last):
            yield last[0]
            last = [it.next() for it in its]

        for i in indices[:-1]:
            if last[i] < last[i+1]:
                last[i] = its[i].next()
            if last[i] > last[i+1]:
                last[i+1] = its[i+1].next()

def search(q):
    tids = [terms.get(term, None) for term in tokenize(q)]
    its = map(iter, (postings[tid] for tid in tids if tid > None))
    return ((score(i, tids), docs[i]) for i in intersect(its)) if its else []

def format(q):
    for hit in sorted(search(q)): print "%2.3f %s" % hit

if len(sys.argv) != 2:
    print >> sys.stderr, "Usage:", sys.argv[0], "<root dir>"
else:
    index_dir(sys.argv[1])
    while True: format(raw_input('Query? '))
