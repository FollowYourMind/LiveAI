from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
database = SqliteExtDatabase('../umiA.sqlite3', autocommit=False, journal_mode='persist')
database.connect()
# database = SqliteDatabase('/Users/masaMikam/Dropbox/Project/umiA/umiA.sqlite3', **{})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

# class SqliteSequence(BaseModel):
#     name = UnknownField(null=True)  # 
#     seq = UnknownField(null=True)  # 

#     class Meta:
#         db_table = 'sqlite_sequence'

class Srtrtemps(BaseModel):
    kanasstream = CharField(db_column='kanasStream', null=True)
    lenrule = IntegerField(db_column='lenRule', null=True)
    losecnt = IntegerField(null=True)
    name = CharField(primary_key=True)
    totalcnt = IntegerField(null=True)
    wincnt = IntegerField(null=True)
    wordsstream = CharField(db_column='wordsStream', null=True)

    class Meta:
        db_table = 'srtrtemps'

class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)

    class Meta:
        db_table = 'tweets'

class Users(BaseModel):
    auth = CharField(null=True)
    cnt = IntegerField(null=True)
    context = CharField(null=True)
    createdat = DateTimeField(db_column='createdAt')
    exp = IntegerField(null=True)
    fav_cnt = IntegerField(null=True)
    followers_cnt = IntegerField(null=True)
    friends_cnt = IntegerField(null=True)
    mode = CharField(null=True)
    name = CharField(null=True)
    other = CharField(null=True)
    recentid = CharField(db_column='recentID', null=True)
    reply = CharField(db_column='reply_id', null=True)
    reply_name = CharField(null=True)
    replycnt = IntegerField(null=True)
    screen_name = CharField(null=True, primary_key=True)
    status = CharField(db_column='status_id', null=True)
    statuses_cnt = IntegerField(null=True)
    time = CharField(null=True)
    totalcnt = IntegerField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    usr = CharField(db_column='usr_id', null=True)
    waiting = CharField(null=True)

    class Meta:
        db_table = 'users'

class Words(BaseModel):
    head = CharField()
    length = IntegerField()
    tail = CharField()
    word = CharField(primary_key=True)
    yomi = CharField()

    class Meta:
        db_table = 'words'

