class Accounts:
    _TABLE = 'accounts'

    def __init__(self, db, migrator):
        self._db = db
        self._migrator = migrator

    def _init(self):
        self._migrator.apply_migrations(self._TABLE, {
            '20151104': self._create_table
        })

    def list(self):
        self._init()

        query = """
        select "name", "type" from "{s._TABLE}"
        """.format(s=self)
        rows = (sqlite3.Row(c, r) for r in self._db.execute(query))
        return (Account(row['name'], row['type']) for row in rows)

    def create(self, name, type_):
        if not name or ':' in name:
            raise InvalidNameError()

        insert = """
        insert into "{s._TABLE}" ("name", "type") values (?, ?)
        """.format(s=self)
        self._db.execute(insert, name, type_)

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
