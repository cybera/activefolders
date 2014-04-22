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
    home_dtn = peewee.TextField(null=True)

    def path(self):
        path = conf.settings['dtnd']['storage_path'] + '/' + self.uuid
        return path


class FolderDestination(BaseModel):
    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()

    class Meta:
        # Each destination can only exist once per folder
        indexes = (
            (('folder', 'destination'), True),
        )


class Transfer(BaseModel):
    PENDING = 'pending'
    FOLDER_CREATED = 'folder_created'
    IN_PROGRESS = 'in_progress'
    COMPLETE = 'complete'
    ACKNOWLEDGED = 'acknowledged'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (FOLDER_CREATED, 'Folder created'),
        (IN_PROGRESS, 'In progress'),
        (COMPLETE, 'Complete'),
        (ACKNOWLEDGED, 'Acknowledged'),
    )

    folder = peewee.ForeignKeyField(Folder)
    destination = peewee.TextField()
    active = peewee.BooleanField(default=False)
    status = peewee.TextField(default=PENDING, choices=STATUS_CHOICES)
    to_dtn = peewee.BooleanField()

    class Meta:
        # Only one pending and one active transfer per folder destination
        indexes = (
            (('folder', 'destination', 'active'), True),
        )


def init():
    database.init(conf.settings['dtnd']['db_path'])
    Transfer.create_table(fail_silently=True)
    FolderDestination.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
