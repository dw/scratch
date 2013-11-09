
import acid.meta
import gevent
import urlparse
import socket
import hashlib
import gevent.pool
import json
import gevent.subprocess as subprocess
import publicsuffix
import tempfile
import pygeoip


psl = publicsuffix.PublicSuffixList()
asnum = pygeoip.GeoIP('geo/GeoIPASNum.dat')


def resolve(name):
    try:
        return socket.gethostbyname(name)
    except socket.gaierror, e:
        print 'Lookup failed: %r (%s)' % (name, e)


def url_netloc(url):
    parsed = urlparse.urlparse(url)
    return parsed.netloc


class MyModel(acid.meta.Model):
    pass


class Host(MyModel):
    META_REPR_FIELDS = ['name']

    name = acid.meta.String()
    checked = acid.meta.Bool()
    error_count = acid.meta.Integer()
    last_error = acid.meta.String()

    @acid.meta.index
    def by_unchecked(self):
        if not self.checked:
            return True

    @acid.meta.index
    def by_error_count(self):
        return self.error_count


_asn_cache = {}


class HostResult(MyModel):
    host_id = acid.meta.Integer()
    urls = acid.meta.List()

    @acid.meta.index
    def asns(self):
        for url in self.urls:
            pass


class Resource(MyModel):
    host_id = acid.meta.Integer()
    url = acid.meta.String()
    asn = acid.meta.String()

    @acid.meta.key
    def key(self):
        return self.host_id, hashlib.sha1(self.url).digest()

    @property
    def target(self):
        return psl.get_public_suffix(url_netloc(self.url))

    @acid.meta.index
    def by_target_host_id(self):
        return self.target, self.host_id

    @acid.meta.index
    def by_asn_host_id(self):
        return self.asn, self.host_id


def load_hosts():
    for line in open('qc1m.txt'):
        if line.startswith('#') or not line.strip():
            continue
        _, host = line.rstrip('\r\n').split('\t')
        if host == 'Hidden profile':
            continue
        Host(name=host).save()


#store = acid.open('plyvel:hosts.lmdb', txn_context=acid.core.GeventTxnContext)
store = acid.open('lmdb:hosts.lmdb', txn_context=acid.core.GeventTxnContext)

MyModel.bind_store(store)


def do_work(host):
    url = 'http://www.' + host.name
    args = ['stdbuf', '-o1M', 'phantomjs', 'dump-url-resources.js', url]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()

    with store.begin(write=True):
        for line in stdout.splitlines():
            try:
                msg, data = json.loads(line)
            except ValueError:
                print 'Failed JS was: %r' % (line,)
                print 'Host was:', host
                raise

            if msg == 'request' and not data['url'].startswith('data:'):
                addr = resolve(url_netloc(data['url']))
                asn = asnum.org_by_name(addr) if addr else None
                resource = Resource(host_id=host.key[0],
                                    url=data['url'],
                                    asn=asn)
                resource.save()
    print 'done', host


def worker(host):
    try:
        do_work(host)
    except Exception, e:
        host.last_error = str(e)
        host.error_count = (host.error_count or 0) + 1
        print 'Failed:', host
        raise
        with store.begin(write=True):
            host.save()


def generator():
    import gevent.local
    lo = gevent.local.local()
    lo.tid = 1
    with store.begin(write=True):
        Host.by_unchecked.find()
    with store.begin():
        for host in Host.by_unchecked.values(max=1000):
            pool.wait_available()
            pool.add(gevent.spawn(worker, host))



if __name__ == '__main__':
    with store.begin(write=True):
        for resource in iter(Resource.find, None):
            print 'Deleting', resource
            resource.delete()
        print

    pool = gevent.pool.Pool(size=200)
    gevent.spawn(generator).join()
    pool.join()
