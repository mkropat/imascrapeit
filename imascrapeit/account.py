from contextlib import closing
from sqlite3 import Row

class Accounts:
    _TABLE = 'accounts'

    def __init__(self, db):
        self._db = db

    def init(self, migrator):
        migrator.apply(self._db, self._TABLE, {
            '20151104': self._create_table
        })

    def get(self, name):
        query = """
        select "name", "type" from "{s._TABLE}" where "name" = ?
        """.format(s=self)
        with closing(self._db.cursor()) as c:
            c.execute(query, [name])
            row = c.fetchone()
            if row is None:
                raise KeyError(name)
            else:
                row = Row(c, row)
                return Account(row['name'], row['type'])

    def __contains__(self, name):
        query = """
        select 1 from "{s._TABLE}" where "name" = ?
        """.format(s=self)
        r = self._db.execute(query, [name])
        return r.fetchone() is not None

    def list(self):
        query = """
        select "name", "type" from "{s._TABLE}" order by "name"
        """.format(s=self)
        with closing(self._db.cursor()) as c:
            rows = (Row(c, r) for r in c.execute(query))
            return [Account(row['name'], row['type']) for row in rows]

    def create(self, name, type_):
        if not name or ':' in name:
            raise InvalidNameError()

        insert = """
        insert into "{s._TABLE}" ("name", "type") values (?, ?)
        """.format(s=self)
        self._db.execute(insert, (name, type_))

    def __delitem__(self, name):
        query = """
        delete from "{s._TABLE}" where "name" = ?
        """.format(s=self)
        self._db.execute(query, [name])

    @classmethod
    def _create_table(klass, db):
        db.execute("""
        create table "{k._TABLE}" (
            "name" text not null,
            "type" text not null,
            unique ("name")
        )
        """.format(k=klass))

class Account:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_

class InvalidNameError(Exception): pass
