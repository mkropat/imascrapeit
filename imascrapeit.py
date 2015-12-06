import contextlib
import itertools
import os.path
import sqlite3
import sys
import webbrowser

# pip install babel chromedriver_installer cryptography Flask marshmallow python-dateutil selenium watchdog

from imascrapeit import dirs
from imascrapeit.balance import BalanceEntry, BalanceHistory
from imascrapeit.chrome import open_chrome
from imascrapeit.clients import ally, bbt
from imascrapeit.creds import CredStore
from imascrapeit.duration import minutes
from imascrapeit.store import DbMigrator

import backend

def main():
    #webbrowser.open('http://localhost:{port}/'.format(port=port))
    backend.run()

def get_balances():
    creds = CliCredShell(dirs.settings())
    accounts = [backend.Account(t, creds[t]) for t in sys.argv[1:]]

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

if __name__ == '__main__':
    main()
