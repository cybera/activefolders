import peewee
import datetime
import json
import activefolders.conf as conf
from uuid import UUID

database = peewee.SqliteDatabase(None, fields={'text': 'text'}, threadlocals=True)


class JsonSerializer:
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
    destination = peewee.TextField()
    credentials = JsonField(null=True)
    check_for_results = peewee.BooleanField(default=False)
    result_files = JsonField(null=True)
    results_folder = peewee.ForeignKeyField(Folder, related_name='results_for', null=True)
    results_retrieved = peewee.BooleanField(default=False)
    initial_results = peewee.BooleanField(default=False)
    tries_without_changes = peewee.IntegerField(default=0)

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
    folder = peewee.ForeignKeyField(Folder)
    dtn = peewee.TextField()
    active = peewee.BooleanField(default=False)

    class Meta:
        # Only one pending and one active transfer per folder destination
        indexes = (
            (('folder', 'dtn', 'active'), True),
        )


class Request(BaseModel):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    METHODS = (
        (GET, 'GET'),
        (POST, 'POST'),
        (DELETE, 'DELETE'),
    )

    method = peewee.TextField(choices=METHODS)
    dtn = peewee.TextField()
    command = peewee.TextField()
    headers = JsonField(null=True)
    params = JsonField(null=True)
    data = JsonField(null=True)
    expected_responses = JsonField(null=True)
    dtn = peewee.TextField()
    failures = peewee.IntegerField(default=0)

    class Meta:
        indexes = (
            (('command', 'headers', 'params', 'data', 'dtn'), True),
        )


def init():
    database.init(conf.settings['dtnd']['db_path'])
    Transfer.create_table(fail_silently=True)
    Export.create_table(fail_silently=True)
    FolderDestination.create_table(fail_silently=True)
    Folder.create_table(fail_silently=True)
    Request.create_table(fail_silently=True)
