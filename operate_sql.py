#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from setup import core_sql, talk_sql, twlog_sql, wordnet_sql
from sql_models import *
import natural_language_processing
# import dialog_generator
import _
from _ import p, d, MyObject, MyException
import threading
from contextlib import contextmanager
# @_.timeit
@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_ss(url, texts):
    data_source = [{'url': url, 'text': text} for text in texts]
    # SS.insert_many(row_dicts).execute()
    # @db.atomic()
    for data_dict in data_source:
        SS.create(**data_dict)


@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_ss(url):
    datas = SS.select().where(SS.url ==  url).order_by(SS.time.desc()).limit(100)
    return datas

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_ss_dialog(person = '', kw = '', n = 1000):
    dialogs = SSdialog.select().where(SSdialog.person == person, SSdialog.text.contains(kw)).limit(n)
    return dialogs

def get_ss_dialog_within(person = '', kw = 'カバン', n = 1000):
    dialogs = SSdialog.select().where(SSdialog.text.contains(kw)).limit(n)
    def _func(obj):
        try:
            rel_obj = SSdialog_relation.select().where(SSdialog_relation.id2 == obj.id).get()
        except DoesNotExist:
            return None
        try:
            if not person:
                response_obj = SSdialog.select().where(SSdialog.id == rel_obj.id3).get()
            else:
                response_obj = SSdialog.select().where(SSdialog.id == rel_obj.id3, SSdialog.person == person).get()
        except DoesNotExist:
            return None
        return obj.text, response_obj.text
    return _.compact([_func(dialog_obj) for dialog_obj in dialogs])
    
reg = natural_language_processing.RegexTools()
def save_ss_dialog(url):
    @_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
    @db.atomic()
    def _save_ssdialog():
        datas = SS.select().where(SS.url ==  url).order_by(SS.time.desc()).limit(100)
        text = ''.join([data.text for data in datas])
        dialog_ls = reg.extract_discorse(text)
        id_ls = []
        for dialog in dialog_ls:
            dialog['url'] = url
            ss_dialog = SSdialog.create(**dialog)
            id_ls.append(ss_dialog.id)
        trigrams = _.convert_gram(id_ls, n_gram = 3)
        [SSdialog_relation.create(id1 = trigram[0], id2 = trigram[1], id3 = trigram[2]) for trigram in trigrams]
        return True
    return _save_ssdialog()

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_stats(stats_dict = {'whose': 'sys', 'status': '', 'number': 114514}):
    t = Stats.create(**stats_dict)
    return t

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_stats(whose = 'sys', status = '', n = 100):
    stats_data = Stats.select().where(Stats.whose ==  whose, Stats.status == status).order_by(Stats.time.desc()).limit(n)
    data_ls = [(data.number, data.time) for data in stats_data]
    return data_ls

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def upsert_core_info(whose_info = '', info_label = '', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True):
    core_info, is_created = CoreInfo.get_or_create(whose_info = whose_info, info_label = info_label, defaults = kwargs)
    if is_update:
        update = CoreInfo.update(**kwargs).where(CoreInfo.whose_info ==whose_info, CoreInfo.info_label == info_label)
        update.execute()
    return core_info

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_task(taskdict = {'who':'kaihatsu_paka', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.now(JST)}):
    t = Task.create(**taskdict)
    return t

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def search_tasks(when = datetime.now(), who = None, n = 10):
    active = Task.select().where(~Task.status == 'end')
    if who is None:
        tasks = active.where(Task.when < when).order_by(Task.id.desc()).limit(n)
    else:
        tasks = active.where(Task.when < when, Task.who == who).order_by(Task.id.desc()).limit(n)
    return tasks


# @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = False)
@_.retry((apsw.BusyError, apsw.CantOpenError), tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def update_task(taskid = None, who_ls = [], kinds = [], taskdict = {'who':'', 'what': 'call', 'to_whom': '_apkX', 'when': datetime.now(JST)}):
    if not kinds:
        task = Task.update(**taskdict).where(Task.id == taskid)
    elif who_ls:
        if not taskid:
            task = Task.update(**taskdict).where(Task.what << kinds, Task.who << who_ls)
        else:
            task = Task.update(**taskdict).where(Task.id == taskid, Task.what << kinds, Task.who << who_ls)
    else:
        if not taskid:
            task = Task.update(**taskdict).where(Task.what << kinds)
        else:
            task = Task.update(**taskdict).where(Task.id == taskid, Task.what << kinds)
    task.execute()
    return True

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def del_tasks(status = 'end'):
    tasks = Task.select().where(Task.status == status)
    [task.delete_instance() for task in tasks]

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def upsert_shiritori(name = '', kwargs = {'kana_stream': '', 'word_stream': ''}, is_update = True):
    core_info, is_created = ShiritoriModel.get_or_create(name = name, defaults = kwargs)
    if is_update:
        update = ShiritoriModel.update(**kwargs).where(ShiritoriModel.name == name)
        update.execute()
    return core_info



#####twlog_sql#######
# @_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_tweet_status(status, is_display = True):
    try:
        tweetstatus = TweetStatus.create(_id = status['id_str'], data = status)
        if not is_display:
            return tweetstatus
        elif not status['in_reply_to_screen_name'] is None:
            print(''.join([status['user']['name'], '|\n@', status['in_reply_to_screen_name'], status['text'], '\n++++++++++++++++++++++++++++++++++']))
        else:
            print(''.join([status['user']['name'], '|\n', status['text'], '\n++++++++++++++++++++++++++++++++++']))
        return tweetstatus
    except:
        return None
@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_twlog(status_id = 1):
    return Tweets.select().where(Tweets.status_id == status_id).get()
@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_twlog_pool(n = 1000):
    tweets = Tweets.select().order_by(Tweets.created_at.desc()).limit(n)
    return [tweet.text for tweet in tweets]

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def get_twlog_users(n = 1000, screen_name = 'chana1031'):
    tweets = Tweets.select().where(Tweets.screen_name == screen_name).order_by(Tweets.created_at.desc()).limit(n)
    return [t for t in [tweet.text for tweet in tweets] if not 'RT' in t and not '@' in t]

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_tweet_dialog(twdialog_dic = {
                'SID' : '',
                'KWs' : '',
                'nameA' : '',
                'textA' : '',
                'nameB' : '',
                'textB' : '',
                'posi' : 1,
                'nega' : 0,
                'bot_id' : 'bot',
                'created_at' : datetime.now(JST),
                'updated_at' : datetime.now(JST)
            }):
        if twdialog_dic:
            twdialog, is_created = TwDialog.create_or_get(**twdialog_dic)
            return twdialog
@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = '')
@db.atomic()
def get_twlog_list(n = 1000, UserList = None, BlackList = [], contains = ''):
    if not UserList is None:
        users_tweets = Tweets.select().where(Tweets.screen_name << UserList, ~Tweets.screen_name << BlackList)
    else:
        users_tweets = Tweets.select().where(~Tweets.screen_name << BlackList)
    tweets = users_tweets.where(~Tweets.text.contains('RT'), ~Tweets.text.contains('【'), Tweets.text.contains(contains)).order_by(Tweets.created_at.desc()).limit(n)
    tweetslist = [_.clean_text(tweet.text) for tweet in tweets]
    return tweetslist

def get_kusoripu(tg1 = 'LiveAI_Alpaca', is_open = False, n = 1000):
    try:
        if not is_open:
            return np.random.choice([ku.phrase for ku in Kusoripu.select().where(~ Kusoripu.phrase.contains('{ID}')).limit(n)])
        else:
            return np.random.choice([ku.phrase for ku in Kusoripu.select().where(Kusoripu.phrase.contains('{ID}')).limit(n)]).format(ID = ''.join(['@', tg1, ' ']))

    except:
        raise DoesNotExist

@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = '')
@db.atomic()
def get_phrase(phrase_type = '', status = '', n = 10, character = 'sys'):
    if character == 'sys':
        Ps = Phrase.select().where(Phrase.status == status).limit(n)
    elif not status:
        Ps = Phrase.select().where(Phrase.phrase_type == phrase_type, Phrase.character == character).limit(n)
    elif not phrase_type:
        Ps = Phrase.select().where(Phrase.status == status, Phrase.character == character).limit(n)
    else:
        Ps = Phrase.select().where(Phrase.phrase_type == phrase_type, Phrase.status == status, Phrase.character == character).limit(n)
    if len(Ps) == 0:
        Ps = Phrase.select().where(Phrase.status == status).limit(n)             
    try:
        return np.random.choice([p.phrase for p in Ps])
    except:
        raise DoesNotExist

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@db.atomic()
def save_phrase(phrase, author = '_mmkm', status = 'mid', phrase_type = 'UserLearn', character = 'sys'):
    P = Phrase.create(phrase = phrase, status = status, phrase_type = phrase_type, author = author)
    return P

# [TODO]
@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = False)
@db.atomic()
def update_phrase(phrase, ratio = 1):
    P = Phrase.select().where(Phrase.phrase == phrase).get()
    P.reputation *= ratio
    P.save()
    return True

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
def data_save(data):
    data.save()

@contextmanager
@db.atomic()
def userinfo_with(screen_name):
    userinfo = None
    try:
        userinfo = get_userinfo(screen_name)
        userinfo.origin_exp = userinfo.exp
        yield userinfo
    finally:
        if userinfo:
            userinfo.total_exp += max(0, userinfo.exp - userinfo.origin_exp)
            data_save(userinfo)

@db.atomic()
def get_userinfo(screen_name):
    userinfo, is_created = Users.get_or_create(screen_name = screen_name, defaults = {
        'name' : screen_name,
        'nickname' : screen_name,
        'time' : datetime.now(JST),
        'user_id' : None,
        'talk_with': '',
        'user_type' : 'person',
        'total_cnt' : 0, 
        'total_reply_cnt' : 0, 
        'total_fav_cnt' : 0, 
        'passwd' : 'undefined',
        'exp' : 0,
        'total_exp': 0,
        'status_id' : '',
        'tmp': ''
        })
    userinfo.is_created = is_created
    return userinfo

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1, jitter=0)
@db.atomic()
def save_userinfo(userstatus):
    userinfo = Users(**userstatus)
    userinfo.save()
    return userstatus

@db.atomic()
def get_userbot(username, botname):
    userbot, is_created = UserBotRelation.get_or_create(username = username, botname = botname, defaults = {
        'mode' : 'dialog',
        'intimacy' : 1,
        'cnt' : 0,
        'reply_cnt': 0,
        'total_cnt' : 0,
        'total_fav_cnt' : 0,
        'total_reply_cnt' : 0,
        'reply_id' : '',
        'status_id' : '',
        'context' : '',
        'time' : datetime.now(JST)
        })
    userbot.is_created = is_created
    return userbot

@db.atomic()
def get_userbot_bytime(delay_min = 30):
    comp_time = datetime.now(JST) - timedelta(minutes = delay_min)
    return UserBotRelation.select().where(UserBotRelation.time < comp_time)

@db.atomic()
def adjust_userbot_max_value():
    users = UserBotRelation.select().where(UserBotRelation.max_intimacy < UserBotRelation.intimacy)
    for user in users:
        user.max_intimacy = max(user.max_intimacy, user.intimacy)
        user.save()

@db.atomic()
def autochange_user_type():
    users = Users.select().where(Users.name.contains('bot') | Users.screen_name.contains('bot')).limit(6000)
    for user in users:
        user.user_type = user.user_type.replace('person', '')
        if not 'bot' in user.user_type:
            user.user_type += 'bot'
        user.save()

@db.atomic()
def rank_userbot(botnames = [], n = 1000):
    if not botnames:
        return UserBotRelation.select().order_by(UserBotRelation.intimacy.desc()).limit(n)
    else:
        return UserBotRelation.select().where(UserBotRelation.botname << botnames).order_by(UserBotRelation.intimacy.desc()).limit(n)


@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = 'データがありません。')
@db.atomic()
def rank_intimacy(username, botname = '', nickname = 'あなた',is_partition = False, n = 500):
    ans = ''
    userbot = UserBotRelation.select().where(UserBotRelation.username == username, UserBotRelation.botname == botname).get()
    if not is_partition:
        ans = '\n【全体 親密度順位】\n'
        higher_ub = UserBotRelation.select().where(userbot.intimacy < UserBotRelation.intimacy)
        ranked_ubs = rank_userbot(botnames = [], n = n)
    else:
        ans = '\n【キャラ別 親密度順位「' + botname + '」】\n'
        higher_ub = UserBotRelation.select().where(UserBotRelation.botname == botname, userbot.intimacy < UserBotRelation.intimacy)
        ranked_ubs = rank_userbot(botnames = [botname], n = n)  
    rank = higher_ub.count()
    if rank == 0:
        lower_ranker1 = ranked_ubs[rank+1]
        ans += '        《祝 '+ nickname +'がNO.1!!》\n\n' + str(rank+1) + '位 '+ nickname + '&' + botname + '♡' +str(round(userbot.intimacy, 2))+ '\n        -' + str(round(userbot.intimacy- lower_ranker1.intimacy, 3)) + '\n' + str(rank+2) + '位 '+ lower_ranker1.username + '&' + lower_ranker1.botname + '♡' + str(round(lower_ranker1.intimacy, 2))
    elif rank + 3 > n:
        bound_ranker = ranked_ubs[n-1]
        ans += str(n) + '位 '+ bound_ranker.username + '&' + bound_ranker.botname + '♡' + str(round(bound_ranker.intimacy, 2)) + '\n        〜圏外〜\n        +' + str(round(bound_ranker.intimacy - userbot.intimacy, 3)) + '\n' + str(rank+1) + '位 ' + nickname + '&' + botname + '♡' +str(round(userbot.intimacy, 2))
    else:
        higher_ranker1 = ranked_ubs[rank-1]
        lower_ranker1 = ranked_ubs[rank+1]
        ans += str(rank) + '位 '+ higher_ranker1.username + '&' + higher_ranker1.botname + '♡' + str(round(higher_ranker1.intimacy, 2)) + '\n        +' + str(round(higher_ranker1.intimacy - userbot.intimacy, 3)) + '\n' + str(rank+1) + '位 ' + nickname + '&' + botname + '♡' +str(round(userbot.intimacy, 2))+ '\n        -' + str(round(userbot.intimacy- lower_ranker1.intimacy, 3)) + '\n' + str(rank+2) + '位 '+ lower_ranker1.username + '&' + lower_ranker1.botname + '♡' + str(round(lower_ranker1.intimacy, 2))
    return ans

# def rank_userinfo(user_types = ['person', 'quasi-bot'], n = 1000):
#     return Users.select().where(Users.user_type << user_types).order_by(Users.total_exp.desc()).limit(n)

@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = 'データがありません。')
@db.atomic()
def rank_exp(username, user_types = ['person', 'quasi-bot'], nickname = 'あなた', is_totalexp = False, n = 500):
    ans = ''
    userinfo = Users.select().where(Users.screen_name == username).get()
    if not is_totalexp:
        ans = '\n【現在EXP順位】\n'
        higher_ub = Users.select().where(Users.user_type << user_types, userinfo.exp < Users.exp)
        ranked_ubs = Users.select().where(Users.user_type << user_types).order_by(Users.exp.desc()).limit(n)
    else:
        ans = '\n【累計EXP順位】\n'
        higher_ub = Users.select().where(Users.user_type << user_types, userinfo.total_exp < Users.total_exp)
        ranked_ubs = Users.select().where(Users.user_type << user_types).order_by(Users.total_exp.desc()).limit(n)
    rank = higher_ub.count()
    if rank == 0:
        lower_ranker1 = ranked_ubs[rank+1]
        if not is_totalexp:
            user_exp = userinfo.exp
            l_exp = lower_ranker1.exp
        else:
            user_exp = userinfo.total_exp
            l_exp = lower_ranker1.total_exp    
        ans += '《祝 '+ nickname + 'がNO.1!!》\n\n' + str(rank+1) + '位 '+ nickname + str(user_exp)+ 'EXP\n        -' + str(user_exp - l_exp) + '\n' + str(rank+2) + '位 '+ lower_ranker1.nickname + str(l_exp) + 'EXP'
    elif rank + 3 > n:
        bound_ranker = ranked_ubs[n-1]
        if not is_totalexp:
            user_exp = userinfo.exp
            b_exp = bound_ranker.exp
            l_exp = lower_ranker1.exp
        else:
            user_exp = userinfo.total_exp
            b_exp = bound_ranker.total_exp
            l_exp = lower_ranker1.total_exp
        ans += str(n) + '位 '+ bound_ranker.nickname + str(b_exp) + 'EXP\n        〜圏外〜\n        +' + str(b_exp - user_exp) + '\n' + str(rank+1) + '位 ' + nickname + str(user_exp) + 'EXP'
    else:
        higher_ranker1 = ranked_ubs[rank-1]
        lower_ranker1 = ranked_ubs[rank+1]
        if not is_totalexp:
            user_exp = userinfo.exp
            h_exp = higher_ranker1.exp
            l_exp = lower_ranker1.exp
        else:
            user_exp = userinfo.total_exp
            h_exp = higher_ranker1.total_exp
            l_exp = lower_ranker1.total_exp
        ans += str(rank) + '位 '+ higher_ranker1.nickname + str(h_exp) + 'EXP\n        +' + str(h_exp - user_exp) + '\n' + str(rank+1) + '位 ' + nickname + str(user_exp)+ 'EXP\n        -' + str(user_exp - l_exp) + '\n' + str(rank+2) + '位 '+ lower_ranker1.nickname + str(l_exp) + 'EXP'
    return ans


@contextmanager
@db.atomic()
def userbot_with(username, botname):
    userbot = None
    try:
        userbot = get_userbot(username, botname)
        userbot.origin_reply_cnt = userbot.reply_cnt
        userbot.origin_cnt = userbot.cnt
        yield userbot
    finally:
        if userbot:
            userbot.total_reply_cnt += min(max(0, userbot.reply_cnt - userbot.origin_reply_cnt), 2)
            userbot.total_cnt += min(max(0, userbot.cnt - userbot.origin_cnt), 2)
            data_save(userbot)

@_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
@_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = None)
@db.atomic()
def get_wordnet_result(lemma):
    @_.retry(apsw.BusyError, tries=10, delay=0.3, max_delay=None, backoff=1.2, jitter=0)
    @_.forever(exceptions = DoesNotExist, is_print = False, is_logging = False, ret = [])
    @db.atomic()
    def _convert_synset_into_words(target_synset):
        same_sense_set = Sense.select().where(Sense.synset == target_synset).limit(n)
        same_sense_wordid_ls = [same_sense_word.wordid for same_sense_word in same_sense_set]
        same_sense_words = Word.select().where(Word.wordid << same_sense_wordid_ls, Word.lang << langs_ls).limit(n)
        same_sense_lemma_ls = [same_sense_word.lemma for same_sense_word in same_sense_words]
        return same_sense_lemma_ls
    n = 10
    # langs_ls = ['jpn', 'eng']
    langs_ls = ['jpn']
    wn_relation = {}
    W = Word.select().where(Word.lemma == lemma).get()
    selected_wordid = W.wordid
    wn_sense = Sense.select().where(Sense.wordid == selected_wordid).get()
    selected_synset = wn_sense.synset
    coordinated_lemma_ls = _convert_synset_into_words(target_synset = selected_synset)
    synlinks = Synlink.select().where(Synlink.synset1 == selected_synset).limit(n)
    wn_relation = {link: words_ls for link, words_ls in [(synlink.link, _convert_synset_into_words(target_synset = synlink.synset2))  for synlink in synlinks] if words_ls}
    wn_relation['coordinate'] = coordinated_lemma_ls
    return wn_relation
class BotProfile(MyObject):
    def __init__(self, bot_id = ''):
        self.bot_id = bot_id
        self.screen_name = self.bot_id
        self.read()
    def save(self):
        upsert_core_info(whose_info = self.bot_id, info_label = 'name', kwargs = {'Char1': self.name, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
        upsert_core_info(whose_info = self.bot_id, info_label = 'description', kwargs = {'Char1': self.description, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
        upsert_core_info(whose_info = self.bot_id, info_label = 'location', kwargs = {'Char1': self.location, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
        upsert_core_info(whose_info = self.bot_id, info_label = 'url', kwargs = {'Char1': self.url, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
        upsert_core_info(whose_info = self.bot_id, info_label = 'abs_icon_filename', kwargs = {'Char1': self.abs_icon_filename, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
        upsert_core_info(whose_info = self.bot_id, info_label = 'abs_banner_filename', kwargs = {'Char1': self.abs_banner_filename, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
    def read(self):
        self.name = upsert_core_info(whose_info = self.bot_id, info_label = 'name', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
        self.description = upsert_core_info(whose_info = self.bot_id, info_label = 'description', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
        self.location = upsert_core_info(whose_info = self.bot_id, info_label = 'location', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
        self.url = upsert_core_info(whose_info = self.bot_id, info_label = 'url', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
        self.abs_icon_filename = upsert_core_info(whose_info = self.bot_id, info_label = 'abs_icon_filename',kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
        self.abs_banner_filename = upsert_core_info(whose_info = self.bot_id, info_label = 'abs_banner_filename', kwargs = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
#####talk_sql#######

@db.atomic()
def count_words():
    wordscnt = TFIDFModel.select().where(TFIDFModel.hinshi << ['名詞', '固有名詞'], TFIDFModel.yomi != '*', ~TFIDFModel.hinshi2 << ['数', '接尾']).    count()
    return wordscnt
@db.atomic()
def add_quiz(status):
    Quiz.get_or_create(tag = 'test', question = '始皇帝の名', answer = '政', author = 'paka')

import crawling
@db.atomic()
def add_eitango(word, username = 'paka'):
    ans = crawling.search_weblioEJJE(word = word)
    if ans:
        Quiz.get_or_create(tag = '英単語', question = word, answer = ans, author = username)
    return ans
@db.atomic()
def n_taku_quiz(tag = ['test', '英単語'], form_cnt = 4):
    quizes = Quiz.select().where(Quiz.tag << tag)
    if quizes.count() == 0:
        ans =  'データ不足'
    quize_dic = {quize.question: quize.answer for quize in quizes if quize.answer != 'undefined' and quize.question != 'undefined'}
    questions = quize_dic.keys()
    answers = quize_dic.values()
    _question = np.random.choice(list(set(questions)))
    _correct_ans = quize_dic[_question]
    listset_anss = list(set(answers))
    choice_cnt = min(len(listset_anss), form_cnt)
    _anss = np.random.choice(listset_anss, choice_cnt, replace=False)
    ans = ''.join(['[問]: ', _question])
    i = 0
    for i in range(choice_cnt):
        if len(_anss[i]) > 10:
            _anss[i] = ''.join([_anss[i][:10], '...'])
        ans += ''.join(['\n', str(i+1), '. ', _anss[i]])
    return ans

@db.atomic()
def dl2db(url, filename = None, _format = None, owner = None):
    folder_tree = url.split('/')
    if filename is None:
        filename = folder_tree[-1]
    if _format is None:
        _format = ''.join(folder_tree[-1].split('.')[1:])
    with urllib.request.urlopen(url) as response:
        _data = response.read()
        sql_data, is_created = BinaryBank.create_or_get(_id = uuid.uuid4(), filename = filename, _format = _format, url = url, data = _data, owner = owner)
        return sql_data._id

@db.atomic()
def file2db(filepath = testpic, filename = None, _format = None, owner = None):
    folder_tree = filepath.split('/')
    if filename is None:
        filename = folder_tree[-1]
    if _format is None:
        _format = ''.join(folder_tree[-1].split('.')[1:])
    with open(filepath, 'rb') as file:
        _data = file.read()
        p(type(_data))
        sql_data, is_created = BinaryBank.create_or_get(_id = uuid.uuid4(), filename = filename, _format = _format, url = filepath, data = _data, owner = owner)
        return sql_data._id

@_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = None)
@db.atomic()
def db2file(_id = '97658366-aa50-44d2-aa7f-3906745ef137', folderpath = None, filename = None):
    _data = BinaryBank.select().where(BinaryBank._id == _id).get()
    if folderpath is None:
        folderpath = '/'.join([_.get_thispath(), 'tmp'])
    if not os.path.exists(folderpath):
            os.mkdir(folderpath)
    if filename is None:
        filename = _data.filename
    if not '.' in filename:
        filename = '.'.join([filename, _data._format]) 
    filepath = '/'.join([folderpath, filename])
    with open(filepath, 'wb') as file:
        file.write(_data.data)
    return filepath

def save_medias2db(status):
  try:
    medias = status['extended_entities']['media']
    screen_name = status['user']['screen_name']
    return [dl2db(url = ''.join([media['media_url'], ':orig']), filename = None, _format = None, owner = screen_name) for media in medias]
  except Exception as e:
    print(e)

if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    # imgdata = 
    # save_medias(status)
    # url = 'http://pubdocs.worldbank.org/en/369791465266160108/060616-procurement-guideline-meeting-ECFA.pdf'
    # dl2db(url)
    # status = TweetStatus.select().where(TweetStatus._id == '772457619415904256').get()
    # save_medias2db(status.data)
    # file2db()
    
    files = _.get_deeppath_dic(DIR = '/Users/masaMikam/Desktop/imgs/animebkup/')
    for file in files:
    	filepath = '/Users/masaMikam/Desktop/imgs/animebkup/' + file[0]
    	file2db(filepath = filepath, filename = None, _format = None, owner = None)
    # a = get_phrase(phrase_type = '', status = '', n = 10, character = '海未')
    # p(a)
    # dl2db(url = 'http://pbs.twimg.com/media/Crl_GbTUIAAAYKn.jpg', filename = None, _format = None, owner = None)
    # filepath = db2file(_id = 'MjAxNjA5MDUwMjMzNTIvNDQ1Mw==', folderpath = None, filename = 'tmp')
    # p(filepath)
    # url  = 'http://articleimage.nicoblomaga.jp/image/151/2014/d/5/d58c986045b90af8e42e495668c42f75247a290e1400313998.jpg'
    # sql_data = dl2db(url = url , filename = None, _format = None)
    # p(sql_data._id)
    # sql_data = BinaryBank.select().where(BinaryBank._id == 'MjAxNjA5MDUwMjMzNTIvNDQ1Mw==').get()
    # p(sql_data.data)
    # file2db(filepath = '/Users/masaMikam/Downloads/46481697.jpeg')
    # statuses = TweetStatus.select().where(TweetStatus.status['status_id'] == '114514').limit(3)
    # for status in statuses:
    #     p(status.status)
    # p(n_taku_quiz(tag = ['test', '英単語'], form_cnt = 4))
    # users = UserBotRelation.select().where(UserBotRelation.reply_cnt > -1).limit(6000)
    # users = Users.select().where(Users.name.contains('bot') | Users.screen_name.contains('bot')).limit(6000)
    # for user in users:
    #     user.user_type = 'bot'
    # autochange_user_type()
    #     p(user.username)
    #     # user.passwd = 'undefined'
    #     user.cnt = 0
    #     user.reply_cnt = 0
    #     # user.total_cnt = max(user.total_reply_cnt, user.cnt)
    #     user.save()
    # with userinfo_with(screen_name = 'kaihatsu_paka') as userinfo:
    #     p(userinfo.__dict__)
    #     userinfo.exp -= 10
        # userinfo.total_exp += max(0, userinfo.exp - userinfo.origin_exp)
    # adjust_userbot_max_value()
    # s = get_userbot_bytime(delay_min = 30)
    # if 7+ int(s[0].intimacy)/10 < 10:
    #     p('a')

    # q, is_created = Quiz.get_or_create(tag = 'test', question = '始皇帝の名', answer = '政', author = 'paka')
    # p(q.__dict__)
    # quizes = Quiz.select().where(Quiz.tag << ['test']).limit(50)
    # text = '始皇帝の名前は？'
    # p(natural_language_processing.NLPdatas(text).main.summary.akkusativ)

    # for a in s:
        # p(a.username)
    # ranks = rank_userbot([])
    # ans = ''
    # total_intimacy = np.sum([rank.intimacy for rank in ranks])
    # for rank in range(1000):
    #     userbot = ranks[rank]
    #     ans += str(rank+1)+'位 '+ userbot.username + '&' + userbot.botname + '♡' + str(round(userbot.intimacy, 2)) + '\n'
    # p(ans)
    # a = get_ss_dialog_within(person = '', kw = 'カバン', n = 1000)
    # s = get_ss_dialog(person = '凛', kw = '流行って', n = 1000)
    # p([(a.username, a.intimacy) for a in s])

    # with userbot_with('all_bad_rin', '穂乃果') as a:
    #     import numpy as np
    #     p(str(round(a.intimacy, 2)))
    #     float_intimacy = float(a.intimacy)
    #     a.intimacy = float_intimacy + np.log2(120 - float_intimacy) /50
        # a.intimacy = float_intimacy / 1.005
    # task = save_task(taskdict = {'who':'kaihatsu_paka', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()})
    # p(task.id)
    # t = Task.select().where(Task.id == str(task.id)).get()
    # t.status = 'end'
    # t.save()
    # p(search_tasks(when = datetime.now(), who = None, n = 10))

    # update_task(taskid = None, who_ls = [], kinds = [], taskdict = {'who':'', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()})
    # save_stats(stats_dict = {'whose': 'sys', 'status': '', 'number': 114514})

    # p(get_stats(whose = 'LiveAI_Umi', status = 'time_line_cnt', n = 100))
    # a = np.random.choice(get_twlog_users(n = 100, screen_name = 'ci_nq'))
    # a = get_wordnet_result('日本')
    # bp = BotProfile('LiveAI_Umi')
    # bp.read()
    # p(bp)
    # a = upsert_core_info(whose_info = 'LiveAI_Umi', info_label = 'abs_banner_filename', kwargs = {'Char1': '/Users/masaMikam/Desktop/Data/user/LiveAI_Umi/kaihatsu_paka_20160605015744_banner.jpg', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)._data['Char1']
    # a = get_phrase(status = 'kusorip', character = 'sys')
    # p(a)
    # p(locals())
    # a = search_tasks(when = datetime.now(), who = 'kaihatsu_paka', n = 10)
    # # p(get_twlog_pool(10))
    # lock = None
    # del_tasks()
    # save_task(taskdict = {'who':'test', 'what': 'tweet', 'to_whom':'AAA'})
    # update_task(taskid = 211, taskdict = {'status': 'end'})
    # umis = get_ss_dialog(person = '海未', n = 100000)
    # # [umi.delete_instance() for umi in umis]
    # p( [umi.text for umi in umis])

    # for i in range(500):
    # while True:
    # p([ku.phrase for ku in Kusoripu.select().where(Kusoripu.phrase.contains('@')).limit(100)])
    # if True:
        # with userinfo_with(screen_name = '例外h_y_ok') as userinfo:
    # with userinfo_with(screen_name = 'h_y_oknbbs') as userinfo:
    #     p(userinfo.__dict__)
    #     userinfo.talk_with = '海未'
    #     with userbot_with(userinfo.screen_name, userinfo.talk_with) as userbot:
    #         p(userbot.__dict__)
                # userinfohy.screen_name = 'h_y_ok'
        # userinfo.name = 'ひよ'
    # save_userinfo(a)


