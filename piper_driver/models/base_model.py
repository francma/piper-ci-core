from peewee import Proxy
from peewee import Model

from piper_driver.addins.exceptions import *

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy
