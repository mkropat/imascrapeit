class DbMigrator:
    def __init__(self, db):
        self._db = db

        self._inited = False

    def _init(self):
        if not self._inited:
            with self._db:
                self._db.execute(self._CREATE_VERSIONS_TABLE)
                self._db.execute(self._INSERT_V20151027)
            self._inited = True

    def apply_migrations(self, table, migrations):
        """Apply a series of migrations to a given table if necessary

        Migrations are expected in a format like:
        {
            '20150102': do_v20150102_func,
            '20150203': do_v20150203_func
        }
        """

        self._init()

        query = """ select "version" from "versions" where "table"=? """

        applied = set(row[0] for row in self._db.execute(query, [table]))
        unapplied = set(migrations.keys()) - applied

        for v in sorted(unapplied):
            self._apply(table, v, migrations[v])

    def _apply(self, table, version, migration_func):
        with self._db: # BEWARE leaky transactions--sqlite only wraps DML in transactions, not DDL
            migration_func(self._db)

            insert = """ insert into "versions" ("table", "version") values (?, ?) """
            self._db.execute(insert, [table, version])

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

