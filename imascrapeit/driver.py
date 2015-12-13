from glob import glob
from importlib import import_module
from os import path

from imascrapeit import clients

def list():
    drivers = [
        {
            'id': n,
            'entry_point': get_factory(n).ENTRY_POINT
        }
        for n in _list_names()
    ]

    return sorted(drivers, key=lambda d: d['id'])

def _list_names():
    def get_name(p):
        filename = path.basename(p)
        return path.splitext(filename)[0]

    clients_dir = path.dirname(clients.__file__)
    modules = glob(path.join(clients_dir, '*.py'))
    names = (get_name(m) for m in modules)
    return (n for n in names if not n.startswith('_'))

def get_factory(name):
    m = import_module('.clients.' + name, __package__);
    return m.new_client

