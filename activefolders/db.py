from peewee import *
from activefolders.config import config

database = SqliteDatabase(config['dtnd']['db_path'])

class BaseModel(Model):
    class Meta:
        database = database

class Folder(BaseModel):
    uuid = CharField(primary_key=True, max_length=36)

def init():
    Folder.create_table(fail_silently=True)
