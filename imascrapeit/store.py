import sqlite3

class DbContext:
    def __init__(self, db, table_factories):
        if isinstance(db, str):
            db = sqlite3.connect(db)

        self._db = db
        self._tables = table_factories.keys()

        for name, factory in table_factories.items():
            setattr(self, name, factory(self._db))

    def init_tables(self, migrator=None):
        if migrator is None:
            migrator = DbMigrator(self._db)

        for name in self._tables:
            getattr(self, name).init(migrator)

    def commit(self):
        self._db.commit()

    def rollback(self):
        self._db.rollback()

    def close(self):
        self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and exc_val is None and exc_tb is None:
            self.commit()
        else:
            self.rollback()

class DbMigrator:
    def __init__(self, version_db):
        self._version_db = version_db

        self._inited = False

    def _init(self):
        if not self._inited:
            with self._version_db:
                self._version_db.execute(self._CREATE_VERSIONS_TABLE)
                self._version_db.execute(self._INSERT_V20151027)
            self._inited = True

    def apply(self, db, table, migrations):
        """Apply a series of migrations to a given table if necessary

        Migrations are expected in a format like:
        {
            '20150102': do_v20150102_func,
            '20150203': do_v20150203_func
        }
        """

        self._init()

        query = """ select "version" from "versions" where "table"=? """

        applied = set(row[0] for row in self._version_db.execute(query, [table]))
        unapplied = set(migrations.keys()) - applied

        for v in sorted(unapplied):
            self._apply(db, table, v, migrations[v])

    def _apply(self, db, table, version, migration_func):
        with self._version_db:
            with db:
                migration_func(db)

                insert = """ insert into "versions" ("table", "version") values (?, ?) """
                self._version_db.execute(insert, [table, version])

    _CREATE_VERSIONS_TABLE = """
    create table if not exists "versions" (
        "table" text not null,
        "version" text not null,
        unique ("table", "version")
    )
    """

    _INSERT_V20151027 = """
    insert or replace into "versions" ("table", "version") values ('versions', '20151027')
    """
