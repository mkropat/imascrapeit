import contextlib, datetime, sqlite3

import dateutil.parser

from .amount import Amount

class BalanceEntry:
    def __init__(self, account, amount, timestamp=None):
        self.account = account
        self.amount = amount
        self.timestamp = self._parse_timestamp(timestamp)

    @staticmethod
    def _parse_timestamp(timestamp):
        if timestamp is None:
            return datetime.datetime.utcnow()
        elif isinstance(timestamp, str):
            return dateutil.parser.parse(timestamp)
        else:
            return timestamp

    def __repr__(self):
        return '{s.account}: {s.amount} @{s.timestamp}'.format(s=self)

class BalanceHistory:
    _TABLE = 'balance_history'

    def __init__(self, db):
        self._db = db

    def init(self, migrator):
        migrator.apply(self._db, self._TABLE, {
            '20151027': self._create_table
        })

    def add(self, entry):
        insert = """
        insert into "{s._TABLE}" ("timestamp", "account", "currency", "amount") values (?, ?, ?, ?)
        """.format(s=self)
        self._db.execute(insert, [
            entry.timestamp.isoformat(),
            entry.account,
            entry.amount.currency,
            str(entry.amount.amount)
        ])

    def list_accounts(self):
        query = """
        select "account" from "{s._TABLE}" group by "account" order by "account"
        """.format(s=self)
        return [r[0] for r in self._db.execute(query)]

    def get_current(self, account):
        query = """
        select "timestamp", "currency", "amount"
        from "{s._TABLE}"
        where "account"=?
        order by "timestamp" desc
        limit 1
        """.format(s=self)
        row = self._fetchone(query, account)

        if row:
            return BalanceEntry(
                account,
                Amount(row['currency'], row['amount']),
                row['timestamp'])
        else:
            return BalanceEntry(account, Amount.null())

    def _fetchone(self, query, *args):
        c = self._db.cursor()
        row = c.execute(query, args).fetchone()
        if row:
            return sqlite3.Row(c, row)

    @classmethod
    def _create_table(klass, db):
        db.execute("""
        create table "{k._TABLE}" (
            "timestamp" text not null,
            "account" text not null,
            "currency" text not null,
            "amount" text not null
        )
        """.format(k=klass))
