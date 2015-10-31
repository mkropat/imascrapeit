import contextlib, importlib, itertools, os.path, sqlite3, sys

# pip install babel chromedriver_installer cryptography python-dateutil selenium watchdog

from . import dirs
from .balance import BalanceEntry, BalanceHistory
from .chrome import open_chrome
from .clients import ally, bbt
from .creds import CredShell
from .duration import minutes
from .store import DbMigrator

def main():
    creds = CredShell(dirs.settings())
    accounts = [_Account(t, creds[t]) for t in sys.argv[1:]]

    db_dir = os.path.join(dirs.settings(), 'history.db')
    with contextlib.closing(sqlite3.connect(db_dir)) as db:
        migrator = DbMigrator(db)
        history = BalanceHistory(db, migrator)

        _fetch_and_store_balances(accounts, history)

        balances = [history.get_current(a) for a in history.list_accounts()]
        for b in balances:
            print(b.account + ':', b.amount)

        print('---------')
        print('Balance:', sum([e.amount for e in balances]))

class _Account:
    def __init__(self, name, creds=None, type_=None):
        self.name = name
        self._creds = creds

        if type_ is None:
            type_ = self.name
        self.type_ = type_

        self.client = None

    def new_client(self, browser, timeout=None):
        m = importlib.import_module('.clients.' + self.type_, __package__)
        new_client = getattr(m, 'new_client')
        return new_client(browser, self._creds, timeout)

def _fetch_and_store_balances(accounts, history):
    if accounts:
        with open_chrome(dirs.chrome_profile('ImaScrapeIt Profile')) as browser:
            for a in accounts:
                client = a.new_client(browser, timeout=minutes(5))
                bal = client.get_balance()
                history.add(BalanceEntry(a.name, bal))

def _print_transactions():
    entries = _combine(
        bbt.import_transactions(sys.argv[1]),
        ally.import_transactions(sys.argv[2]))

    for row in sorted(entries.values(), key=lambda e: e.timestamp):
        print(row)

def _combine(*dicts):
    return dict(itertools.chain.from_iterable([d.items() for d in dicts]))

main()
