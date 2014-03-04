from peewee import *
import activefolders.config as config

deferred_db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = deferred_db

class Folder(BaseModel):
    uuid = CharField(primary_key=True, max_length=36)

def init():
    deferred_db.init(config.config['dtnd']['db_path'])
    Folder.create_table(fail_silently=True)
