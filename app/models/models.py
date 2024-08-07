import datetime
import pytz

import peewee

from data.config import DATABASE_FILE

base = peewee.SqliteDatabase(DATABASE_FILE)


class BaseModel(peewee.Model):
    class Meta:
        database = base


class User(BaseModel):
    cid = peewee.IntegerField(unique=True)
    refer = peewee.IntegerField(default=0)
    invested = peewee.FloatField(default=0)
    collected = peewee.DateTimeField(default=datetime.datetime.now())
    storaged = peewee.FloatField(default=0)
    balance = peewee.FloatField(default=0)
    ref_balance = peewee.FloatField(default=0)
    username = peewee.CharField(default="Юзернейм скрыт")
    fullname = peewee.CharField(default="Без имени")
    registered = peewee.DateTimeField(default=datetime.datetime.now())
    alerts = peewee.BooleanField(default=True)

    def __str__(self):
        return f'{self.cid} [{self.id}]'


class Payment(BaseModel):
    cid = peewee.IntegerField()
    done = peewee.BooleanField(default=False)


class UserHistory(BaseModel):
    cid = peewee.IntegerField()
    amount = peewee.FloatField()
    editor = peewee.IntegerField(default=0)
    created = peewee.DateTimeField(default=datetime.datetime.now())


base.connect()
base.create_tables([User, UserHistory, Payment])
