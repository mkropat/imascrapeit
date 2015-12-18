from collections import namedtuple
from uuid import uuid4

Account = namedtuple('Account', [
    'id',
    'name',
    'driver',
    'username'
])

class Accounts:
    _TABLE = 'accounts'

    def __init__(self, db):
        self._db = db

    def init(self, migrator):
        migrator.apply(self._db, self._TABLE, {
            '20151215': self._create_table,
        })

    def __getitem__(self, id_):
        query = """
        select "id", "name", "driver", "username" from "{s._TABLE}" where "id" = ?
        """.format(s=self)
        row = self._db.execute(query, [id_]).fetchone()
        if row is None:
            raise KeyError(id_)
        else:
            return Account(*row)

    def __contains__(self, id_):
        query = """
        select 1 from "{s._TABLE}" where "id" = ?
        """.format(s=self)
        r = self._db.execute(query, [id_])
        return r.fetchone() is not None

    def list(self):
        query = """
        select "id", "name", "driver", "username" from "{s._TABLE}" order by "name"
        """.format(s=self)
        return [Account(*row) for row in self._db.execute(query)]

    def create(self, name, driver, username):
        insert = """
        insert into "{s._TABLE}" ("id", "name", "driver", "username") values (?, ?, ?, ?)
        """.format(s=self)
        account = Account(str(uuid4()), name, driver, username)
        self._db.execute(insert, account)
        return account

    def __delitem__(self, id_):
        query = """
        delete from "{s._TABLE}" where "id" = ?
        """.format(s=self)
        self._db.execute(query, [id_])

    @classmethod
    def _create_table(klass, db, **kwargs):
        db.execute("""
        create table "{k._TABLE}" (
            "id" text not null,
            "name" text not null,
            "driver" text not null,
            "username" text not null,
            unique ("id"),
            unique ("driver", "username")
        )
        """.format(k=klass))
