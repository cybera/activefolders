from peewee import *

database = SqliteDatabase('/tmp/dtnd.db')

class BaseModel(Model):
    class Meta:
        database = database

class Folder(BaseModel):
    uuid = CharField(primary_key=True, max_length=36)

def init():
    Folder.create_table(fail_silently=True)
