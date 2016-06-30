

class Series(object):
    # extents() -> deferred(low_ts, high_ts)
    # gets(start_ts, count) -> deferred([val, ...])
    # getRange(low_ts, high_ts) -> deferred([val, ...])
    pass


class SeriesStore(object):
    # openSeries(name, resolution) -> deferred(Series)
    # deleteSeries(name, resolution=None) -> deferred()
    pass
