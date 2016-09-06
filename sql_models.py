#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
#DBs
DATADIR = '/Users/masaMikam/Desktop/Data'

from playhouse.postgres_ext import PostgresqlExtDatabase, BinaryJSONField
db = PostgresqlExtDatabase(database='LiveAI', user='masaMikam')
def uuid_generater():
    random.seed()
    return uuid.uuid4()
#     return base64.b64encode('/'.join([datetime.now(JST).strftime('%Y%m%d%H%M%S'), str(os.getpid())]).encode('utf-8'))
###################################################
#
# >>>>>>>>WEBDATA_SQL>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################
class SQLModel(Model):
    class Meta:
        database = db

class SS(SQLModel):
    url = TextField(null = True)
    text = TextField(null = True)
    time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'ss'
class SSdialog(SQLModel):
    url = TextField(null = True)
    person = TextField(null = True)
    text = TextField(null = True)
    reaction = TextField(null = True)
    time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'ss_dialog'
class SSdialog_relation(SQLModel):
    id1 = IntegerField(null = True)
    id2 = IntegerField(null = True)
    id3 = IntegerField(null = True)
    class Meta:
        db_table = 'ss_dialog_relation'
        primary_key = CompositeKey('id1', 'id2', 'id3')
###################################################
#
# >>>>>>>>CORE_SQL>>>>>>>>>>>>>>>>>>>>>>>>>>>DATETIME
#
####################################################
class Stats(SQLModel):
    whose = TextField(null = True)
    status = TextField(null = True)
    number = IntegerField(null=True)
    time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'stats'
class CoreInfo(SQLModel):
    whose_info = TextField(null = True)
    info_label= TextField(null = True)
    Char1 = TextField(null=True)
    Char2 = TextField(null=True)
    Char3 = TextField(null=True)
    Int1 = IntegerField(null=True)
    Int2 = IntegerField(null=True)
    Time1 = DateTimeField(null=True)
    Time2 = DateTimeField(null=True)
    class Meta:
        db_table = 'core_info'
        primary_key = CompositeKey('whose_info', 'info_label')
class ShiritoriModel(SQLModel):
    name = TextField(primary_key=True)
    mode = TextField(null=True)
    kana_stream = TextField(null=True)
    word_stream = TextField(null=True)
    len_rule = IntegerField(null=True)
    tmp = TextField(null=True)
    tmp_cnt = IntegerField(null=True)
    tmp_time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'shiritori'
class CharacterStatusModel(SQLModel):
    name = TextField(primary_key=True)
    nickname= TextField(null=True)
    mode = TextField(null=True)
    exp = IntegerField(null=True)
    character_level = IntegerField(null=True)
    exp_to_level_up = IntegerField(null=True)
    damage = IntegerField(null=True)
    full_hp = IntegerField(null=True)
    rest_hp = IntegerField(null=True)
    hp_gage = TextField(null=True)
    Atk = IntegerField(null=True)
    Def = IntegerField(null=True)
    SpA = IntegerField(null=True)
    SpD = IntegerField(null=True)
    Spe = IntegerField(null=True)
    enemy_name = TextField(null=True)
    class Meta:
         db_table = 'character_status'
class Users(SQLModel):
    screen_name = TextField(primary_key=True)
    user_id = TextField(null=True)
    name = TextField(null=True)
    nickname = TextField(null=True)
    user_type = TextField(null=True)
    passwd = TextField(null=True, default = 'undefined')
    talk_with = TextField(null=True)
    total_cnt = IntegerField(null=True)
    total_fav_cnt = IntegerField(null=True)
    exp = IntegerField(null=True)
    total_exp = IntegerField(null=True)
    status_id = TextField(null=True)
    time = DateTimeField(null=True, default = datetime.now(JST))
    tmp = TextField(null=True)
    class Meta:
        db_table = 'users'

class UserBotRelation(SQLModel):
    botname = TextField(null=True)
    username = TextField(null=True)
    mode = TextField(null=True, default = 'dialog')
    intimacy = DecimalField(max_digits = 10, decimal_places = 5, null = True, default = 1)
    max_intimacy = DecimalField(max_digits = 10, decimal_places = 5, null = True, default = 1)
    cnt = IntegerField(null=True)
    reply_cnt = IntegerField(null=True)
    total_cnt = IntegerField(null=True)
    total_fav_cnt = IntegerField(null=True)
    total_reply_cnt = IntegerField(null=True)
    reply_id = TextField(null=True)
    status_id = TextField(null=True)
    context = TextField(null=True)
    time = DateTimeField(null=True, default = datetime.now(JST))
    tmp = TextField(null=True)
    class Meta:
        db_table = 'userbot_relation'
        primary_key = CompositeKey('botname', 'username')

class UserUserRelation(SQLModel):
    username_from = TextField(null=True)
    username_to = TextField(null=True)
    mode = TextField(null=True, default = 'dialog')
    status_id = TextField(null=True)
    time = DateTimeField(null=True, default = datetime.now(JST))
    tmp = TextField(null=True)
    class Meta:
        db_table = 'useruser_relation'
        primary_key = CompositeKey('username_from', 'username_to')

class Context(SQLModel):
    class Meta:
        db_table = 'context'

class Image(SQLModel):
    _id = TextField(primary_key=True)

    class Meta:
        db_table = 'image'


class Phrase(SQLModel):
    _id = IntegerField(primary_key=True)
    phrase = TextField(null=True)
    phrase_type = TextField(null=True)
    status = TextField(null=True)
    reputation = DecimalField(max_digits = 10, decimal_places = 5, null = True, default = 1)
    author = TextField(null = True)
    character = TextField(null = True)
    created_at = DateTimeField(null=True, default = datetime.now(JST))
    updated_at = DateTimeField(null=True, default = datetime.now(JST))
    class Meta:
        db_table = 'phrase'

class Kusoripu(SQLModel):
    _id = IntegerField(primary_key=True)
    phrase = TextField(null=True)
    reputation = DecimalField(max_digits = 10, decimal_places = 5, null = True, default = 1)
    author = TextField(null = True)
    character = TextField(null = True)
    created_at = DateTimeField(null=True, default = datetime.now(JST))
    class Meta:
        db_table = 'kusoripu'

class Task(SQLModel):
    # _id = TextField(primary_key=True, default = datetime.now(JST)+timedelta(hours = 9))
    status = TextField(null=True, default = 'waiting')
    when = DateTimeField(null=True)
    who = TextField(null=True)
    what = TextField(null=True)
    to_whom = TextField(null=True)
    created_at = DateTimeField(null=True, default = datetime.now(JST))
    tmptext = TextField(null=True, default = '')
    tmpfile = TextField(null=True, default = '')
    tmpcnt = IntegerField(null=True, default = 0)
    tmpid = TextField(null=True, default = '')
    bot_id = TextField(null=True, default = '')
    class Meta:
        db_table = 'task'
###################################################
#
# >>>>>>>>TWLOG_SQL>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################

class Tweets(SQLModel):
    status_id = IntegerField(primary_key=True)
    screen_name = TextField(null=True)
    name = TextField(null=True)
    user_id = TextField(null=True)
    text = TextField(null=True)
    in_reply_to_status_id_str = TextField(null=True)
    bot_id = TextField(null=True)
    createdAt = DateTimeField(null=True)
    updatedAt = DateTimeField(null=True)
    class Meta:
        db_table = 'tweets'

class TwDialog(SQLModel):
    SID = TextField(primary_key=True)
    KWs = TextField(null=True)
    nameA = TextField(null=True)
    textA = TextField(null=True)
    nameB = TextField(null=True)
    textB = TextField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    bot_id = TextField(null=True)
    createdAt = DateTimeField(null=True)
    updatedAt = DateTimeField(null=True)
    class Meta:
        db_table = 'dialog'
###################################################
#
# >>>>>>>>TALK_SQL>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################
class TFIDFModel(SQLModel):
    word = TextField(null=True)
    yomi = TextField(null=True)
    hinshi = TextField(null=True)
    hinshi2  = TextField(null=True)
    info3  = TextField(null=True)
    df = IntegerField(null=True)
    class Meta:
        db_table = 'df'
        primary_key = CompositeKey('word', 'hinshi')

class TrigramModel(SQLModel):
    character = TextField(null=True)
    W1 = TextField(null=True)
    W2 = TextField(null=True)
    W3  = TextField(null=True)
    P1  = TextField(null=True)
    P2 = TextField(null=True)
    P3 = TextField(null=True)
    cnt = IntegerField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    class Meta:
        db_table = 'trigram'
        primary_key = CompositeKey('character', 'W1', 'W2', 'W3')

class FactModel(SQLModel):
    function = TextField(null=True)
    entity = TextField(null=True)
    value  = TextField(null=True)
    akkusativ = TextField(null=True)
    dativ = TextField(null=True)
    character = TextField(null=True)
    cnt = IntegerField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    class Meta:
        db_table = 'facts'

class mSentence(SQLModel):
  framework = TextField(null=True)
  cnt = IntegerField(null=True)
  posi = IntegerField(null=True)
  nega = IntegerField(null=True)
  class Meta:
    db_table = 'meta_sentence'

class mod_pair(SQLModel):
  w_from = TextField(null=True)
  w_to = TextField(null=True)
  w_tag = TextField(null=True)
  cnt = IntegerField(null=True)
  posi = IntegerField(null=True)
  nega = IntegerField(null=True)
  class Meta:
    db_table = 'mod_pair'

###################################################
#
# >>>>>>>>WordNetSQL>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################
class Ancestor(SQLModel):
    hops = IntegerField(null=True)
    synset1 = TextField(index=True, null=True)
    synset2 = TextField(index=True, null=True)

    class Meta:
        db_table = 'ancestor'

class LinkDef(SQLModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    link = TextField(null=True)

    class Meta:
        db_table = 'link_def'

class PosDef(SQLModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    pos = TextField(null=True)

    class Meta:
        db_table = 'pos_def'

class Sense(SQLModel):
    freq = IntegerField(null=True)
    lang = TextField(null=True)
    lexid = IntegerField(null=True)
    rank = TextField(null=True)
    src = TextField(null=True)
    synset = TextField(index=True, null=True)
    wordid = IntegerField(primary_key=True, index=True, null=True)
    class Meta:
        db_table = 'sense'

class Synlink(SQLModel):
    link = TextField(null=True)
    src = TextField(null=True)
    synset1 = TextField(null=True)
    synset2 = TextField(null=True)
    class Meta:
        db_table = 'synlink'
        indexes = (
            (('synset1', 'link'), False),
        )
        primary_key = CompositeKey('synset1', 'link')

class Synset(SQLModel):
    name = TextField(null=True)
    pos = TextField(null=True)
    src = TextField(null=True)
    synset = TextField(primary_key=True, index=True, null=True)

    class Meta:
        db_table = 'synset'

class SynsetDef(SQLModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    sid = TextField(null=True)
    synset = TextField(index=True, null=True)

    class Meta:
        db_table = 'synset_def'

class SynsetEx(SQLModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    sid = TextField(null=True)
    synset = TextField(index=True, null=True)

    class Meta:
        db_table = 'synset_ex'

class Variant(SQLModel):
    lang = TextField(null=True)
    lemma = TextField(null=True)
    varid = PrimaryKeyField(null=True)
    vartype = TextField(null=True)
    wordid = IntegerField(null=True)

    class Meta:
        db_table = 'variant'

class Word(SQLModel):
    lang = TextField(null=True)
    lemma = TextField(index=True, null=True)
    pos = TextField(null=True)
    pron = TextField(null=True)
    wordid = PrimaryKeyField(null=True)
    class Meta:
        db_table = 'word'

class Xlink(SQLModel):
    confidence = TextField(null=True)
    misc = TextField(null=True)
    resource = TextField(null=True)
    synset = TextField(null=True)
    xref = TextField(null=True)

    class Meta:
        db_table = 'xlink'
        indexes = (
            (('synset', 'resource'), False),
        )
class Quiz(SQLModel):
    _id = UUIDField(primary_key = True, default = uuid_generater())
    tag = TextField(default = 'undefined')
    question = TextField(unique = True)
    answer = TextField(default = '')
    author = TextField(default = 'undefined')
    correct_cnt = IntegerField(default = 0)
    incorrect_cnt = IntegerField(default = 0)
    last_at = DateTimeField(default = datetime.now(JST))
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'quiz'

class CrawledData(SQLModel):
    _id = UUIDField(primary_key = True, unique = True, default = uuid_generater())
    tag = TextField(default = 'undefined')
    url = TextField(default = '')
    title = TextField(default = '')
    data = TextField(default = '')
    author = TextField(default = 'undefined')
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'crawled_data'
# class Knowledge(SQLModel):
#     _id = TextField(primary_key = True, unique = True, default = uuid_generater())
#     tag = TextField(default = 'undefined')
#     _from = TextField(default = '')
#     _to = TextField(default = '')
#     author = TextField(default = 'undefined')
#     correct_cnt = IntegerField(default = 0)
#     incorrect_cnt = IntegerField(default = 0)
#     last_at = DateTimeField(default = datetime.now(JST))
#     created_at = DateTimeField(default = datetime.now(JST))
#     class Meta:
#         db_table = 'knowledge'
class TweetStatus(SQLModel):
    _id = TextField(primary_key = True, unique = True, default = uuid_generater())
    data = BinaryJSONField(dumps = None)
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'tweet_status'
class DMStatus(SQLModel):
    _id = TextField(primary_key = True, unique = True, default = uuid_generater())
    data = BinaryJSONField(dumps = None)
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'dm_status'
class EventStatus(SQLModel):
    _id = TextField(primary_key = True, unique = True, default = uuid_generater())
    data = BinaryJSONField(dumps = None)
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'event_status'
class BinaryBank(SQLModel):
    # _id = TextField(primary_key = True, unique = True, default = uuid_generater())
    _id = UUIDField(primary_key = True, unique = True, default = uuid_generater())
    url = TextField(null = True, default = '')
    filename = TextField(null = True, default = '')
    _format =  TextField(null = True, default = '')
    data = BlobField()
    owner = TextField(null = True, default = '')
    json = BinaryJSONField(dumps = None, null = True)
    created_at = DateTimeField(default = datetime.now(JST))
    class Meta:
        db_table = 'binarybank'
if __name__ == '__main__':
    s = '山って知ってる？'
    db.create_tables([BinaryBank], True)

    # import hashlib
    # import base64
    # import random
    # sha256ed_guess_unique_id = hashlib.sha256(datetime.now(JST).strftime('%Y%m%d%H%M%S').encode('utf-8')).hexdigest()
    # unique_id = base64.b64encode('/'.join([datetime.now(JST).strftime('%Y%m%d%H%M%S'), str(os.getpid())]).encode('utf-8'))
    # print(unique_id)
    # print(base64.b64decode(unique_id))
    # a = datetime.now(JST)+timedelta(hours = 9)
    # print(a)
    # import psycopg2

