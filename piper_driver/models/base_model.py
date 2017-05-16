from peewee import Proxy
from peewee import Model

from piper_driver.addins.exceptions import *

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy

    def save(self, force_insert=False, only=None):
        errors = set()
        if hasattr(self, 'validate') and not self.validate(errors):
            raise ModelInvalid(errors=errors)
        super().save(force_insert, only)
