from peewee import Proxy, Model


database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy
