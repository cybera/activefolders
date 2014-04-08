import peewee
import datetime
import activefolders.conf as conf
import activefolders.utils as utils

database = peewee.SqliteDatabase(None, fields={'text': 'text'})


class BaseModel(peewee.Model):
    class Meta:
        database = database


class UUIDField(peewee.Field):
    db_field = 'text'

    def coerce(self, value):
        return utils.coerce_uuid(value)


class Folder(BaseModel):
    uuid = UUIDField(primary_key=True)
    dirty = peewee.BooleanField(default=False)
    last_changed = peewee.DateTimeField(default=datetime.datetime.now)
    home_dtn = peewee.TextField(null=True)

    def path(self):
        path = conf.settings['dtnd']['storage_path'] + '/' + self.uuid
        return path


class FolderDestination(BaseModel):
    # TODO: Make unique key
    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()


class Transfer(BaseModel):
    # TODO: Make unique key
    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()
    pending = peewee.BooleanField(default=False)


def init():
    database.init(conf.settings['dtnd']['db_path'])
    Transfer.create_table(fail_silently=True)
    FolderDestination.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
