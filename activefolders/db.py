import peewee
import datetime
import activefolders.conf as conf
from uuid import UUID

database = peewee.SqliteDatabase(None, fields={'text': 'text'})


class BaseModel(peewee.Model):
    class Meta:
        database = database


class UUIDField(peewee.Field):
    db_field = 'text'

    def coerce(self, value):
        return str(UUID(value))


class Folder(BaseModel):
    uuid = UUIDField(primary_key=True)
    dirty = peewee.BooleanField(default=False)
    last_changed = peewee.DateTimeField(default=datetime.datetime.now)
    home_dtn = peewee.TextField()

    def path(self):
        path = conf.settings['dtnd']['storage_path'] + '/' + self.uuid
        return path


class FolderDestination(BaseModel):
    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()
    credentials = peewee.TextField(null=True)

    class Meta:
        # Each destination can only exist once per folder
        indexes = (
            (('folder', 'destination'), True),
        )


class Export(BaseModel):
    folder_destination = peewee.ForeignKeyField(FolderDestination)
    active = peewee.BooleanField(default=False)

    class Meta:
        indexes = (
            (('folder_destination', 'active'), True),
        )


class Transfer(BaseModel):
    CREATE_FOLDER = 'create_folder'
    IN_PROGRESS = 'in_progress'
    GET_ACKNOWLEDGMENT = 'get_acknowledgement'
    STATUS_CHOICES = (
        (CREATE_FOLDER, 'Creating folder'),
        (IN_PROGRESS, 'In progress'),
        (GET_ACKNOWLEDGMENT, 'Getting acknowledgement'),
    )

    folder = peewee.ForeignKeyField(Folder)
    dtn = peewee.TextField()
    active = peewee.BooleanField(default=False)
    status = peewee.TextField(default=CREATE_FOLDER, choices=STATUS_CHOICES)

    class Meta:
        # Only one pending and one active transfer per folder destination
        indexes = (
            (('folder', 'dtn', 'active'), True),
        )


def init():
    database.init(conf.settings['dtnd']['db_path'])
    Transfer.create_table(fail_silently=True)
    Export.create_table(fail_silently=True)
    FolderDestination.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
