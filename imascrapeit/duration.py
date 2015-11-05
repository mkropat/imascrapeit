import datetime

def minutes(m):
    return _from_duration(m, minutes=m)

def seconds(s):
    return _from_duration(s, seconds=s)

def _from_duration(d, **kwargs):
    if isinstance(d, datetime.timedelta):
        return d
    else:
        return datetime.timedelta(**kwargs)
