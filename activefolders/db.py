from peewee import *
import activefolders.config as config
import activefolders.utils as utils

deferred_db = SqliteDatabase(None, fields={'text': 'text'})


class BaseModel(Model):
    class Meta:
        database = deferred_db


class UUIDField(Field):
    db_field = 'text'

    def coerce(self, value):
        return utils.coerce_uuid(value)


class Folder(BaseModel):
    uuid = UUIDField(primary_key=True)


def init():
    deferred_db.init(config.config['dtnd']['db_path'])
    Folder.create_table(fail_silently=True)
