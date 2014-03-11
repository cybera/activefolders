import peewee
import activefolders.conf as conf
import activefolders.utils as utils

deferred_db = peewee.SqliteDatabase(None, fields={'text': 'text'})


class BaseModel(peewee.Model):
    class Meta:
        database = deferred_db


class UUIDField(peewee.Field):
    db_field = 'text'

    def coerce(self, value):
        return utils.coerce_uuid(value)


class Folder(peewee.BaseModel):
    uuid = peewee.UUIDField(primary_key=True)

    def path(self):
        path = conf.settings['dtnd']['storage_path'] + '/' + self.uuid
        return path


class Transfer(peewee.BaseModel):
    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()
    completed = peewee.BooleanField(default=False)


def init():
    deferred_db.init(conf.settings['dtnd']['db_path'])
    Transfer.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
