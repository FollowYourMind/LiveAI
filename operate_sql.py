#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from setup import core_sql, talk_sql, twlog_sql, wordnet_sql
from sql_models import *
import dialog_generator
import _
from _ import p, d, MyObject, MyException
def save_stats(stats_dict = {'whose': 'sys', 'status': '', 'number': 114514}):
	try:
		core_sql.create_tables([Stats], True)
		with core_sql.transaction():
			t = Stats(**stats_dict)
			t.save()
			core_sql.commit()
	except Exception as e:
		print(e)
		core_sql.rollback()

def get_stats(whose = 'sys', status = '', n = 100):
	try:
		with core_sql.transaction():
			stats_data = Stats.select().where(Stats.whose ==  whose, Stats.status == status).order_by(Stats.time.desc()).limit(n)
			data_ls = [(data.number, data.time) for data in stats_data]
			return data_ls
	except Exception as e:
		print(e)
		core_sql.rollback()
def get_core_info(whose_info = 'LiveAI_Umi', info_label = 'test', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False):
	# core_sql.create_tables([CoreInfo], True)
	try:
		with core_sql.transaction():
			core_info, is_created = CoreInfo.get_or_create(whose_info = whose_info, info_label = info_label)
			if is_created or is_update:
				standard_dic['whose_info'] = whose_info
				standard_dic['info_label'] = info_label
				ci = CoreInfo(**standard_dic)
				ci.save()
				return ci
			return core_info
	except Exception as e:
		print(e)
		if e == 'database is locked':
			p('dddddddddd')
		core_sql.rollback()
def save_task(taskdict = {'who':'_umiS', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()+timedelta(hours = 9)}):
	try:
		core_sql.create_tables([Task], True)
		with core_sql.transaction():
			t = Task(**taskdict)
			t.save()
			core_sql.commit()
			p(''.join(['TASK_SAVED]',taskdict['who'], '_', taskdict['what']]))
	except Exception as e:
		print(e)
		core_sql.rollback()

def search_tasks(when = datetime.now(), who = '_umiS', n = 10):
	try:
		with core_sql.transaction():
			active = Task.select().where(~Task.status == 'end')
			if who == '':
				tasks = active.where(Task.when < when).order_by(Task.id.desc()).limit(n)
			else:
				tasks = active.where(Task.when < when, Task.who == who).order_by(Task.id.desc()).limit(n)
			tasklist = [task.__dict__['_data'] for task in tasks]
			return tasklist
	except Exception as e:
		print(e)
		core_sql.rollback()

def update_task(taskid = None, who_ls = [], kinds = [], taskdict = {'who':'', 'what': 'call', 'to_whom': '_apkX', 'when':datetime.utcnow()}):
	try:
		with core_sql.transaction():
			if who_ls:
				if not kinds:
					task = Task.update(**taskdict).where(Task.id == taskid)
				elif not taskid:
					task = Task.update(**taskdict).where(Task.what << kinds, Task.who << who_ls)
				else:
					task = Task.update(**taskdict).where(Task.id == taskid, Task.what << kinds, Task.who << who_ls)
			else:
				if not kinds:
					task = Task.update(**taskdict).where(Task.id == taskid)
				elif not taskid:
					task = Task.update(**taskdict).where(Task.what << kinds)
				else:
					task = Task.update(**taskdict).where(Task.id == taskid, Task.what << kinds)
			task.execute()
	except Exception as e:
		print(e)
		core_sql.rollback()

#####twlog_sql#######
def save_tweet_status(status, tmp):
	try:
		twlog_sql.create_tables([Tweets], True)
		with twlog_sql.transaction():
			Tweets.create(
				status_id = int(status['id_str']),
				screen_name = status['user']['screen_name'],
				name = status['user']['name'],
				text = status['text'],
				user_id = status['user']['id_str'],
				in_reply_to_status_id_str = status['in_reply_to_status_id_str'],
				bot_id = tmp['bot_id'],
				createdAt = datetime.utcnow(),
				updatedAt = datetime.utcnow()
			)
			twlog_sql.commit()
			# print('SAVED]')
	except Exception as e:
		print(e)
		twlog_sql.rollback()

def get_tweet_dialog(status_id = 1):
	try:
		# twlog_sql.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with twlog_sql.transaction():
			return Tweets.select().where(Tweets.status_id == status_id).get().__dict__['_data']
	except Exception as e:
		print(e)
		twlog_sql.rollback()
		return ''

def save_tweet_dialog(status, tmp, logtext = ''):
	try:
		# twlog_sql.create_tables([TwDialog], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with twlog_sql.transaction():
			if not logtext:
				twlog = Tweets.select().where(Tweets.status_id == int(status['in_reply_to_status_id_str'])).get().__dict__['_data']
				screen_name = twlog['screen_name']
				logtext = _.clean_text(twlog['text'])
				SID = '/'.join([str(twlog['status_id']), status['id_str']])
			else:
				screen_name = tmp['bot_id']
				SID = ''.join([status['id_str'], 'DM'])
			kws = [key[0] for key in TFIDF.calcKWs(logtext, length = 1, needs = {'固有名詞', '名詞'})]
			TwDialog.create(
				SID = SID,
				KWs = '</>'.join(kws),
				nameA = screen_name,
				textA = logtext,
				nameB = status['user']['screen_name'],
				textB = _.clean_text(status['text']),
				posi = 1,
				nega = 0,
				bot_id = tmp['bot_id'],
				createdAt = datetime.utcnow(),
				updatedAt = datetime.utcnow()
			)
			twlog_sql.commit()
			return True
	except Exception as e:
		print(e)
		twlog_sql.rollback()
		return False

def get_twlog_list(n = 1000, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308'], contains = ''):
	try:
		# twlog_sql.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with twlog_sql.transaction():
			if not UserList:
				tweets = Tweets.select().where(Tweets.text.contains(contains), ~Tweets.text.contains('RT'), ~Tweets.screen_name << BlackList, ~Tweets.text.contains('【')).order_by(Tweets.createdAt.desc()).limit(n)
			else:
			 	tweets = Tweets.select().where(Tweets.screen_name << UserList , ~Tweets.screen_name << BlackList, ~Tweets.text.contains('RT'), ~Tweets.text.contains('【')).order_by(Tweets.createdAt.desc()).limit(n)
		tweetslist = [_.clean_text(tweet.text) for tweet in tweets]
		return tweetslist
	except Exception as e:
		print(e)
		twlog_sql.rollback()

def getPhrase(s_type = '', status = '', n = 10, character = 'sys'):
	p('old get_phrase')
	return get_phrase(s_type = s_type, status = status, n = n, character = character)
def get_phrase(s_type = '', status = '', n = 10, character = 'sys'):
	try:
		with core_sql.transaction():
			if character == 'sys':
				Ps = Phrases.select().where(Phrases.status == status).limit(n)
			elif not status:
				Ps = Phrases.select().where(Phrases.s_type == s_type, Phrases.character == character).limit(n)
			elif not s_type:
				Ps = Phrases.select().where(Phrases.status == status, Phrases.character == character).limit(n)
			else:
				Ps = Phrases.select().where(Phrases.s_type == s_type, Phrases.status == status, Phrases.character == character).limit(n)
			if len(Ps) == 0:
				Ps = Phrases.select().where(Phrases.status == status).limit(n)
				return ''.join([np.random.choice([p.phrase for p in Ps]), '\n(代:[', status, ']of\'', character, '\')'])
			else:
				return np.random.choice([p.phrase for p in Ps])

	except Exception as e:
		print(e)
		core_sql.rollback()
		return ''.join(['...:[', status, '] by \'', character, '\''])
def savePhrase(phrase, author = '_mmkm', status = 'mid', s_type = 'UserLearn', character = 'sys'):
	p('old save_phrase')
	return save_phrase(s_type = s_type, author = author, phrase = phrase, status = status, n = n, character = character)
def save_phrase(phrase, author = '_mmkm', status = 'mid', s_type = 'UserLearn', character = 'sys'):
	try:
		core_sql.create_tables([Phrases], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with core_sql.transaction():
			P, is_created = Phrases.get_or_create(phrase = phrase)
			if is_created:
				P.phrase = phrase
				P.framework = phrase
				P.s_type = s_type
				P.status = status
				P.ok_cnt = 1
				P.ng_cnt = 0
				P.author = author
				# P.createdAt
				P.character = character
				P.save()
				core_sql.commit()
				return True
			return True
	except Exception as e:
		print(e)
		core_sql.rollback()
		return False

def eval_phrase(phrase, ok_add = 0, ng_add = 1):
	try:
		# core_sql.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with core_sql.transaction():
			P = Phrases.select().where(Phrases.phrase == phrase).get()
			P.ok_cnt = P.ok_cnt + ok_add
			P.ng_cnt = P.ng_cnt + ng_add
			P.save()
			core_sql.commit()
			return True
	except Exception as e:
		print(e)
		core_sql.rollback()
		return False
def get_userinfo(screen_name):
	return read_userinfo(screen_name = screen_name)

def read_userinfo(screen_name):
	try:
		# core_sql.create_tables([Users], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with core_sql.transaction():
			try:
				userinfo, is_created = Users.get_or_create(screen_name = screen_name)
			except Exception as e:
				if screen_name == 'h_y_ok':
					screen_name = '例外h_y_ok'
					userinfo, is_created = Users.get_or_create(screen_name = screen_name)
				else:
					print(e)
					is_created = False
			if is_created:
				userinfo.name = screen_name
				userinfo.nickname = screen_name
				userinfo.cnt = 0
				userinfo.total_cnt = 0
				userinfo.reply_cnt = 0
				userinfo.exp = 0
				userinfo.mode = 'dialog'
				userinfo.context = ''
				userinfo.time = datetime.utcnow()
			try:
				userinfodata = userinfo._data
			except:
				userinfodata = ''
			return userinfodata, is_created
	except Exception as e:
		print(e)
		core_sql.rollback()

def save_userinfo(userstatus):
	try:
		# core_sql.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with core_sql.transaction():
			try:
				userinfo = Users(**userstatus)
				userinfo.save()
			except Exception as e:
				print(e)
				return False, userstatus
			core_sql.commit()
			return True, userstatus
	except Exception as e:
	  core_sql.rollback()
	  return False, userstatus
def get_wordnet_result(lemma):
	n = 10
	langs_ls = ['jpn', 'eng']
	langs_ls = ['jpn']
	wn_relation = {}
	def convert_synset_into_words(target_synset):
		try:
			same_sense_set = Sense.select().where(Sense.synset == target_synset).limit(n)
			same_sense_wordid_ls = [same_sense_word.wordid for same_sense_word in same_sense_set]
			same_sense_words = Word.select().where(Word.wordid << same_sense_wordid_ls, Word.lang << langs_ls).limit(n)
			same_sense_lemma_ls = [same_sense_word.lemma for same_sense_word in same_sense_words]
			return same_sense_lemma_ls
		except:
			return []
	try:
		with wordnet_sql.transaction():
			W = Word.select().where(Word.lemma == lemma).get()
			selected_wordid = W.wordid
			wn_sense = Sense.select().where(Sense.wordid == selected_wordid).get()
			selected_synset = wn_sense.synset
			coordinated_lemma_ls = convert_synset_into_words(target_synset = selected_synset)
			synlinks = Synlink.select().where(Synlink.synset1 == selected_synset).limit(n)
			wn_relation = {link: words_ls for link, words_ls in [(synlink.link, convert_synset_into_words(target_synset = synlink.synset2))  for synlink in synlinks] if words_ls}
			wn_relation['coordinate'] = coordinated_lemma_ls
			return wn_relation
	except Exception as e:
		print(e)
		wordnet_sql.rollback()
class BotProfile(MyObject):
	def __init__(self, bot_id = 'a'):
		self.bot_id = bot_id
		self.read()
	def save(self):
		get_core_info(whose_info = self.bot_id, info_label = 'name', standard_dic = {'Char1': self.name, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
		get_core_info(whose_info = self.bot_id, info_label = 'description', standard_dic = {'Char1': self.description, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
		get_core_info(whose_info = self.bot_id, info_label = 'location', standard_dic = {'Char1': self.location, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
		get_core_info(whose_info = self.bot_id, info_label = 'url', standard_dic = {'Char1': self.url, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
		get_core_info(whose_info = self.bot_id, info_label = 'abs_icon_filename', standard_dic = {'Char1': self.abs_icon_filename, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
		get_core_info(whose_info = self.bot_id, info_label = 'abs_banner_filename', standard_dic = {'Char1': self.abs_banner_filename, 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)
	def read(self):
		self.name = get_core_info(whose_info = self.bot_id, info_label = 'name', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
		self.description = get_core_info(whose_info = self.bot_id, info_label = 'description', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
		self.location = get_core_info(whose_info = self.bot_id, info_label = 'location', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = True)._data['Char1']
		self.url = get_core_info(whose_info = self.bot_id, info_label = 'url', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
		self.abs_icon_filename = get_core_info(whose_info = self.bot_id, info_label = 'abs_icon_filename', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
		self.abs_banner_filename = get_core_info(whose_info = self.bot_id, info_label = 'abs_banner_filename', standard_dic = {'Char1': '', 'Char2': '', 'Char3': '', 'Int1':0, 'Int2':0}, is_update = False)._data['Char1']
if __name__ == '__main__':
	# umi = read_userinfo('h_y_ok')
	# umi = get_twlog_list(n = 10)
	# umi = get_phrase(status = 'ぬるぽ', n = 1)
	# p(umi)
	# a= get_wordnet_result('米')
	bp = BotProfile('a')
	# bp.name = 'てすとおととおお'
	# bp.save()
	p(bp)
	# a =read_userinfo(screen_name = 'masaMikam')[0]._data
	# p(a)
	status = {'favorite_count': 0, 'created_at': 'Wed Feb 17 14:54:01 +0000 2016', 'contributors': None, 'truncated': False, 'in_reply_to_user_id_str': None, 'retweet_count': 0, 'id': 699970059683414016, 'in_reply_to_status_id_str': None, 'geo': None, 'entities': {'hashtags': [], 'urls': [], 'symbols': [], 'user_mentions': []}, 'id_str': '691170059683414016', 'in_reply_to_screen_name': None, 'is_quote_status': False, 'timestamp_ms': '1455720841700', 'coordinates': None, 'in_reply_to_status_id': None, 'filter_level': 'low', 'retweeted': False, 'in_reply_to_user_id': None, 'source': '<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>', 'favorited': False, 'user': {'protected': False, 'created_at': 'Sun Mar 31 01:35:13 +0000 2013', 'utc_offset': 32400, 'favourites_count': 27, 'follow_request_sent': None, 'following': None, 'profile_image_url': 'http://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'profile_background_tile': False, 'description': '名前:つゆり きさめ/学生ラブライバー/絶叫勢/ぼっち勢/海未推し/善子推し(仮)/このすば/めぐみんはいいぞ/内田彩/詳細はツイプロ/+aで最近FFの比例がおかしい事に気がついたんでスパムを除く人に見つけ次第フォロー返してます。', 'profile_text_color': '333333', 'friends_count': 1481, 'time_zone': 'Tokyo', 'profile_sidebar_border_color': 'BDDCAD', 'profile_image_url_https': 'https://pbs.twimg.com/profile_images/681463777951236096/SbnleYeJ_normal.jpg', 'screen_name': 'tuyuri_kisame', 'default_profile_image': False, 'statuses_count': 40262, 'name': '栗花落 樹雨', 'is_translator': False, 'profile_background_image_url_https': 'https://abs.twimg.com/images/themes/theme16/bg.gif', 'followers_count': 1921, 'location': '神奈川県東部', 'geo_enabled': False, 'verified': False, 'notifications': None, 'profile_banner_url': 'https://pbs.twimg.com/profile_banners/1317490188/1455626298', 'listed_count': 33, 'profile_background_color': '9AE4E8', 'profile_sidebar_fill_color': 'DDFFCC', 'profile_link_color': '0084B4', 'default_profile': False, 'url': 'http://twpf.jp/tuyuri_kisame', 'profile_use_background_image': True, 'contributors_enabled': False, 'id': 1317490188, 'lang': 'ja', 'id_str': '1317490188', 'profile_background_image_url': 'http://abs.twimg.com/images/themes/theme16/bg.gif'}, 'place': None, 'text': 'トサカのないことりちゃん…( ˘ω˘ )', 'lang': 'ja'}
	# save_tweet_status(status)
	s = '酒'


