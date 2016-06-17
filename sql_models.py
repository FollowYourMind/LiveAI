#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
#DBs
DATADIR = '/Users/masaMikam/Desktop/Data'
twlog_sql_PLACE = DATADIR + '/SQL/sys.twlog'
core_sql_PLACE = DATADIR + '/SQL/sys.info'
talk_sql_PLACE = DATADIR + '/SQL/sys.talk'
wordnet_sql_PLACE = DATADIR + '/lib/wnjpn.db'

from playhouse.sqlite_ext import SqliteExtDatabase
core_sql = SqliteExtDatabase(core_sql_PLACE, autocommit=False, journal_mode='persist')
talk_sql = SqliteExtDatabase(talk_sql_PLACE, autocommit=False, journal_mode='persist')
twlog_sql = SqliteExtDatabase(twlog_sql_PLACE, autocommit=False, journal_mode='persist')
wordnet_sql =  SqliteExtDatabase(wordnet_sql_PLACE, autocommit=False, journal_mode='persist')
###################################################
#
# >>>>>>>>CORE_SQL>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################
class CoreSQLModel(Model):
    class Meta:
        database = core_sql
class Stats(CoreSQLModel):
    whose = CharField(null = True)
    status = CharField(null = True)
    number = IntegerField(null=True)
    time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'stats'
class CoreInfo(CoreSQLModel):
    whose_info = CharField(null = True)
    info_label= CharField(null = True)
    Char1 = CharField(null=True)
    Char2 = CharField(null=True)
    Char3 = CharField(null=True)
    Int1 = IntegerField(null=True)
    Int2 = IntegerField(null=True)
    Time1 = DateTimeField(null=True)
    Time2 = DateTimeField(null=True)
    class Meta:
        db_table = 'core_info'
        primary_key = CompositeKey('whose_info', 'info_label')
class ShiritoriModel(CoreSQLModel):
    name = CharField(primary_key=True)
    mode = CharField(null=True)
    kana_stream = CharField(null=True)
    word_stream = CharField(null=True)
    len_rule = IntegerField(null=True)
    tmp = CharField(null=True)
    tmp_cnt = IntegerField(null=True)
    tmp_time = DateTimeField(null=True, default = datetime.now())
    class Meta:
        db_table = 'shiritori'
class CharacterStatusModel(CoreSQLModel):
    name = CharField(primary_key=True)
    nickname= CharField(null=True)
    mode = CharField(null=True)
    exp = IntegerField(null=True)
    character_level = IntegerField(null=True)
    exp_to_level_up = IntegerField(null=True)
    damage = IntegerField(null=True)
    full_hp = IntegerField(null=True)
    rest_hp = IntegerField(null=True)
    hp_gage = CharField(null=True)
    Atk = IntegerField(null=True)
    Def = IntegerField(null=True)
    SpA = IntegerField(null=True)
    SpD = IntegerField(null=True)
    Spe = IntegerField(null=True)
    enemy_name = CharField(null=True)
    class Meta:
         db_table = 'character_status'
class Users(CoreSQLModel):
    screen_name = CharField(primary_key=True)
    user_id = CharField(null=True)
    name = CharField(null=True)
    nickname = CharField(null=True)
    mode = CharField(null=True)
    cnt = IntegerField(null=True)
    reply_cnt = IntegerField(null=True)
    total_cnt = IntegerField(null=True)
    context = CharField(null=True)
    exp = IntegerField(null=True)
    reply_id = CharField(null=True)
    select_chara = CharField(null=True)
    status_id = CharField(null=True)
    time = DateTimeField(null=True, default = datetime.utcnow())
    tmp = CharField(null=True)
    tmpFile = CharField(null=True)
    tmpTime = DateTimeField(null=True)
    class Meta:
        db_table = 'users'

class Phrases(CoreSQLModel):
    phrase = CharField(null=True)
    framework = CharField(null=True)
    s_type = CharField(null=True)
    status = CharField(null=True)
    ok_cnt = IntegerField(null=True)
    ng_cnt = IntegerField(null=True)
    author = CharField(null = True)
    character = CharField(null = True)
    createdAt = DateTimeField(null=True, default = datetime.utcnow())
    updatedAt = DateTimeField(null=True, default = datetime.utcnow())
    class Meta:
        db_table = 'phrases'
class Task(CoreSQLModel):
    status = CharField(null=True, default = 'waiting')
    when = DateTimeField(null=True)
    who = CharField(null=True)
    what = CharField(null=True)
    to_whom = CharField(null=True)
    createdAt = DateTimeField(null=True, default = datetime.utcnow()+timedelta(hours = 9))
    updatedAt = DateTimeField(null=True, default = datetime.utcnow()+timedelta(hours = 9))
    tmptext = CharField(null=True, default = '')
    tmpfile = CharField(null=True, default = '')
    tmpcnt = IntegerField(null=True, default = 0)
    tmpid = CharField(null=True, default = '')
    bot_id = CharField(null=True, default = '')
    class Meta:
        db_table = 'tasks'
###################################################
#
# >>>>>>>>TWLOG_SQL>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################
class twlog_sqlModel(Model):
    class Meta:
        database = twlog_sql
class Tweets(twlog_sqlModel):
    status_id = IntegerField(primary_key=True)
    screen_name = CharField(null=True)
    name = CharField(null=True)
    user_id = CharField(null=True)
    text = CharField(null=True)
    in_reply_to_status_id_str = CharField(null=True)
    bot_id = CharField(null=True)
    createdAt = DateTimeField(null=True)
    updatedAt = DateTimeField(null=True)
    class Meta:
        db_table = 'tweets'

class TwDialog(twlog_sqlModel):
    SID = CharField(primary_key=True)
    KWs = CharField(null=True)
    nameA = CharField(null=True)
    textA = CharField(null=True)
    nameB = CharField(null=True)
    textB = CharField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    bot_id = CharField(null=True)
    createdAt = DateTimeField(null=True)
    updatedAt = DateTimeField(null=True)
    class Meta:
        db_table = 'dialog'
###################################################
#
# >>>>>>>>TALK_SQL>>>>>>>>>>>>>>>>>>>>>>>>>>>
#
####################################################

class TalkSQLModel(Model):
    class Meta:
        database = talk_sql
class TFIDFModel(TalkSQLModel):
    word = CharField(null=True)
    yomi = CharField(null=True)
    hinshi = CharField(null=True)
    hinshi2  = CharField(null=True)
    info3  = CharField(null=True)
    df = IntegerField(null=True)
    class Meta:
        db_table = 'df'
        primary_key = CompositeKey('word', 'hinshi')

class TrigramModel(TalkSQLModel):
    character = CharField(null=True)
    W1 = CharField(null=True)
    W2 = CharField(null=True)
    W3  = CharField(null=True)
    P1  = CharField(null=True)
    P2 = CharField(null=True)
    P3 = CharField(null=True)
    cnt = IntegerField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    class Meta:
        db_table = 'trigram'
        primary_key = CompositeKey('character', 'W1', 'W2', 'W3')

class FactModel(TalkSQLModel):
    function = CharField(null=True)
    entity = CharField(null=True)
    value  = CharField(null=True)
    akkusativ = CharField(null=True)
    dativ = CharField(null=True)
    character = CharField(null=True)
    cnt = IntegerField(null=True)
    posi = IntegerField(null=True)
    nega = IntegerField(null=True)
    class Meta:
        db_table = 'facts'

class mSentence(TalkSQLModel):
  framework = CharField(null=True)
  cnt = IntegerField(null=True)
  posi = IntegerField(null=True)
  nega = IntegerField(null=True)
  class Meta:
    db_table = 'meta_sentence'

class mod_pair(TalkSQLModel):
  w_from = CharField(null=True)
  w_to = CharField(null=True)
  w_tag = CharField(null=True)
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

class WordNetModel(Model):
    class Meta:
        database = wordnet_sql

class Ancestor(WordNetModel):
    hops = IntegerField(null=True)
    synset1 = TextField(index=True, null=True)
    synset2 = TextField(index=True, null=True)

    class Meta:
        db_table = 'ancestor'

class LinkDef(WordNetModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    link = TextField(null=True)

    class Meta:
        db_table = 'link_def'

class PosDef(WordNetModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    pos = TextField(null=True)

    class Meta:
        db_table = 'pos_def'

class Sense(WordNetModel):
    freq = IntegerField(null=True)
    lang = TextField(null=True)
    lexid = IntegerField(null=True)
    rank = TextField(null=True)
    src = TextField(null=True)
    synset = TextField(index=True, null=True)
    wordid = IntegerField(primary_key=True, index=True, null=True)
    class Meta:
        db_table = 'sense'

class Synlink(WordNetModel):
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

class Synset(WordNetModel):
    name = TextField(null=True)
    pos = TextField(null=True)
    src = TextField(null=True)
    synset = TextField(primary_key=True, index=True, null=True)

    class Meta:
        db_table = 'synset'

class SynsetDef(WordNetModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    sid = TextField(null=True)
    synset = TextField(index=True, null=True)

    class Meta:
        db_table = 'synset_def'

class SynsetEx(WordNetModel):
    def_ = TextField(db_column='def', null=True)
    lang = TextField(null=True)
    sid = TextField(null=True)
    synset = TextField(index=True, null=True)

    class Meta:
        db_table = 'synset_ex'

class Variant(WordNetModel):
    lang = TextField(null=True)
    lemma = TextField(null=True)
    varid = PrimaryKeyField(null=True)
    vartype = TextField(null=True)
    wordid = IntegerField(null=True)

    class Meta:
        db_table = 'variant'

class Word(WordNetModel):
    lang = TextField(null=True)
    lemma = TextField(index=True, null=True)
    pos = TextField(null=True)
    pron = TextField(null=True)
    wordid = PrimaryKeyField(null=True)
    class Meta:
        db_table = 'word'

class Xlink(WordNetModel):
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
if __name__ == '__main__':
    s = ''


