import peewee
import datetime
import json
import activefolders.conf as conf
from uuid import UUID

database = peewee.SqliteDatabase(None, fields={'text': 'text'})


class JsonSerializer(object):
    __json_public__ = None
    __json_hidden__ =  None
    __json_modifiers__ = None

    def to_json(self):
        field_names = self._meta.get_field_names()
        public = self.__json_public__ or field_names
        hidden =  self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        return rv


class BaseModel(peewee.Model, JsonSerializer):
    class Meta:
        database = database


class UUIDField(peewee.Field):
    db_field = 'text'

    def coerce(self, value):
        return str(UUID(value))


class JsonField(peewee.Field):
    db_field = 'text'

    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        return json.loads(value)


class Folder(BaseModel):
    uuid = UUIDField(primary_key=True)
    dirty = peewee.BooleanField(default=False)
    home_dtn = peewee.TextField()
    results = peewee.BooleanField(default=False)

    def path(self):
        path = conf.settings['dtnd']['storage_path'] + '/' + self.uuid
        return path


class FolderDestination(BaseModel):
    folder = peewee.ForeignKeyField(Folder, related_name='destinations')
    results_folder = peewee.ForeignKeyField(Folder, related_name='results_for', null=True)
    results_retrieved = peewee.BooleanField(default=False)
    destination = peewee.TextField()
    credentials = JsonField(null=True)
    result_files = JsonField(null=True)
    check_for_results = peewee.BooleanField(default=False)

    class Meta:
        # Each destination can only exist once per folder
        indexes = (
            (('folder', 'destination'), True),
        )


class ResultsStatus(BaseModel):
    folder_destination = peewee.ForeignKeyField(FolderDestination, related_name='results_status')
    initial_results = peewee.BooleanField(default=False)
    tries_without_changes = peewee.IntegerField(default=0)


class Export(BaseModel):
    folder_destination = peewee.ForeignKeyField(FolderDestination)
    active = peewee.BooleanField(default=False)

    class Meta:
        indexes = (
            (('folder_destination', 'active'), True),
        )


class Transfer(BaseModel):
    folder = peewee.ForeignKeyField(Folder)
    dtn = peewee.TextField()
    active = peewee.BooleanField(default=False)

    class Meta:
        # Only one pending and one active transfer per folder destination
        indexes = (
            (('folder', 'dtn', 'active'), True),
        )


def init():
    database.init(conf.settings['dtnd']['db_path'])
    ResultsStatus.create_table(fail_silently=True)
    Transfer.create_table(fail_silently=True)
    Export.create_table(fail_silently=True)
    FolderDestination.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
