from peewee import Proxy, Model, SqliteDatabase


database_proxy = Proxy()


class SqliteFKDatabase(SqliteDatabase):
    def initialize_connection(self, conn):
        self.execute_sql('PRAGMA foreign_keys=ON;')


class BaseModel(Model):
    class Meta:
        database = database_proxy
