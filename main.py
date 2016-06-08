#!/usr/bin/env python
# -*- coding:utf-8 -*-

#MY MODULEs
#variables
from setup import *
import natural_language_processing
import _
from _ import p, d, MyObject, MyException
import machine_learning_img
import dialog_generator
import twtr_functions
import opencv_functions
import crawling
import game_functions
import operate_sql
def get_kusoripu(tg1):
	ans = operate_sql.get_phrase(status = 'kusoripu', n = 3000)
	if '{ID}' in ans:
		ans = ans.format(ID= ''.join(['@', tg1, ' ']))
	else:
		ans = ''.join(['@', tg1,' \n', ans])
	if '{name}' in ans:
		ans = ans.format(name= 'アルパカ')
	return ans
def is_kusoripu(s):
    if len(s) < 100:
        return False
    # if s.count('\n') > 6:
    #     return True
    if s.count('\u3000') > 5:
        return True
    if s.count('\t') < 5:
        return True
    emoji_cnt = len(re.findall('[\U0001F0CF-\U000207BF]', s))
    if emoji_cnt > 5:
        return True
    kigou_cnt = len(re.findall('[!-/:-@[-`{-~]', s))
    if kigou_cnt > 20:
        return True
    hankaku_katakana_cnt = len(re.findall('[ｦ-ﾟ]', s))
    if hankaku_katakana_cnt > 7:
        return True
    return False

def is_kusa(s):
    if s.count('w') >15:
        return True
    return False
def extract_cmds_dic(text):
    try:
        reg = '\s*(\w+)\s*([!-/:-@≠\[-`{-~]*)\s*[@#]*(\w+)'
        p = re.compile(reg, re.M)
        reg_ls = p.findall(text)
        text = re.sub(p, '', text)
        #-- と空白で挟まれたものをコマンドにする
        return {reg[1]: reg[3] for reg in reg_ls}, text
    except:
        return {}, text
class Temp(MyObject):
	pass
class Stats(MyObject):
	def __init__(self):
		self.TL_cnt = 0
		self.DM_cnt = 0
		self.tweet_cnt_hour = 0
		self.tweet_cnt_today = 0
class TweetLogPool(MyObject):
	def __init__(self):
		self.my_twlog = []
		self.timeline_twlog = []
		self.directmessage_twlog = []
	def append_and_adjust_timeline_twlog(self, appendage):
		self.timeline_twlog.append(appendage)
		self.timeline_twlog = self.timeline_twlog[-20:]
class StreamResponseFunctions(MyObject):
	def __init__(self, bot_id):
		debug_style = ''
		self.default_character = 'sys'
		if bot_id == 'LiveAI_Umi':
			self.default_character = '海未'
		if bot_id == 'LiveAI_Honoka':
			self.default_character = '穂乃果'
		if bot_id == 'LiveAI_Rin':
			self.default_character = '凛'
		if bot_id == 'LiveAI_Eli':
			self.default_character = '絵里'
		if bot_id == 'LiveAI_Maki':
			self.default_character = '真姫'
		if bot_id == 'LiveAI_Hanayo':
			self.default_character = '花陽'
		if bot_id == 'LiveAI_Alpaca':
			self.default_character = 'sys'
		self.bot_id = bot_id
		self.atmarked_bot_id = ''.join(['@', self.bot_id])
		self.manager_id = '_mmKm'
		self.twf = twtr_functions.TwtrTools(self.bot_id)
		#CLASS
		self.bot_profile = operate_sql.BotProfile(self.bot_id)
		self.tmp = Temp()
		self.twlog_pool = TweetLogPool()
		self.stats = Stats()
		self.tmp.charas = Temp()
		#
		self.bot_dir = DATADIR + '/' + bot_id
		self.is_debug_direct_message = 'dm' in debug_style or 'all' in debug_style
		self.is_debug_tweet = 'tweet' in debug_style or 'all' in debug_style
		self.is_debug_event = 'event' in debug_style or 'all' in debug_style
		if not os.path.exists(self.bot_dir):
			os.mkdir(self.bot_dir)
		# self.tmp_config_place = self.bot_dir + '/tmp_config.json'
		# if not os.path.exists(self.tmp_config_place):
		# 	self = {'user_profile':{'screen_name': bot_id, 'name': '', 'url': '', 'location': '', 'abs_icon_filename':'', 'abs_banner_filename':''}}
			# self.sync_json('config')
		# else:
			# self.sync_json('config', is_save = False)
		# self.tmp_place = self.bot_dir + '/tmp.json'
		# if not os.path.exists(self.tmp_place):
		# 	self.tmp = {'bot_id': bot_id, 'response_exception': }
			# self.sync_json()
		# else:
			# self.sync_json(is_save = False)
	def convert_text_as_character(self, text):
		if self.bot_id == 'LiveAI_Rin':
			text = text.replace('です', 'だにゃ').replace('ます', 'にゃ')
		return text
	def send(self, ans, screen_name = '', imgfile = '', status_id = '', mode = 'dm', try_cnt = 0):
		# self.is_enable_tweet = False
		if self.stats.tweet_cnt_hour is None:
			self.stats.tweet_cnt_hour = 0
		p(self.stats.tweet_cnt_hour)
		# 1時間あたりのツイート数が100を上回る場合、ツイートしない。
		if self.stats.tweet_cnt_hour > 100:
			duration = try_cnt + 1
			set_time = self.sync_now() + timedelta(hours=0, minutes = duration)
			operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': 'tweet', 'to_whom':screen_name, 'when':set_time, 'tmptext': ans, 'tmpid': status_id, 'tmpfile': imgfile, 'tmpcnt': try_cnt +1})
			p('[Tweet.1minAfter] @', screen_name, ' ', ans)
			return False
		else:
			# tweeet 数をインクリメントする
			self.stats.tweet_cnt_hour += 1
		if mode == 'dm':
			return self.twf.send_direct_message(ans, screen_name = screen_name, is_debug = self.is_debug_direct_message, try_cnt = try_cnt)
		elif mode in {'open', 'tweet'}:
			return self.twf.send_tweet(ans, screen_name = screen_name, imgfile = imgfile, status_id = status_id, is_debug = self.is_debug_tweet, try_cnt = try_cnt)
		else:
			p(['??', mode])
		return True
	def default_profile(self):
		try:
			# self.sync_json('config', is_save = False)
			self.twf.update_profile(name = self.bot_profile.name, description = self.bot_profile.description, location= self.bot_profile.location, url = self.bot_profile.url, filename = self.bot_profile.abs_icon_filename, BGfilename = '', Bannerfilename = self.bot_profile.abs_banner_filename)
			return True
		except Exception as e:
			logger.debug(e)
			return False
	def sync_now(self):
		#Japan_Time
		self.now = datetime.utcnow() + timedelta(hours = 9)
		return self.now
	# def sync_json(self, json = None, is_save = True):

		# p(json)
		# try:
		# 	if json is None:
		# 		json_place = self.tmp_place
		# 		json_dic = self.tmp
		# 	else:
		# 		json_dic = self
		# 		json_place = self.tmp_config_place
		# 	backup_json_place = json_place
		# except:
		# 	p('reloading_json')
		# 	is_save = False
		# try:
		# 	if is_save:
		# 		_.save_json(json_dic, json_place)
		# 	if json is None:
		# 		self.tmp = _.get_json(json_place, backup_json_place)
		# 	elif json == 'config':
		# 		self = _.get_json(json_place, backup_json_place)
		# 	return True
		# except:
		# 	return False
	def on_initial_main(self):
		# self.bot_profile = Temp()
		p(self.bot_id+' >> Loading Initial_datas...')
		self.tmp.imitating = self.bot_id
		# self.tmp.bot_id. = self.bot_id
		self.tmp.manager_id = self.manager_id
		self.tmp.bots_list = self.twf.get_listmembers_all(username = self.bot_id, listname = 'BOT')
		self.tmp.KARAMIx2 = self.twf.get_listmembers_all(username = self.bot_id, listname = 'KARAMIx2')
		self.tmp.response_exception = self.twf.get_listmembers_all(username = self.bot_id, listname = 'responseException')
		self.tmp.feedback_exception = self.twf.get_listmembers_all(username = self.bot_id, listname = 'feedbackException')
		self.bots_set = set(self.tmp.bots_list)
		self.karamix2_set = set(self.tmp.KARAMIx2)
		self.response_exception_set = set(self.tmp.response_exception)
		self.feedback_exception_set = set(self.tmp.feedback_exception)
		self.tmp.trendwords_ls = self.twf.getTrendwords()
		self.eew_ids_set = {0}
		self.tmp.friend_ids = {}
		self.tmp.response = ['おはよう', 'おやすみ', 'ぬるぽ']
		p(self.bot_id+' >>Loaded setupDatas! => Loading FriendsIDs...')
	def on_friends_main(self, friends):
		self.tmp.friend_ids = friends
		self.friend_ids_set = set(friends)
		p(self.bot_id+' >>Loaded'+str(len(friends))+'FriendsIDs! => starting Streaming...')
	def check_tmpdatas(self):
		return True
	def construct_func(self, cmds_dic, function = 'add', baseparam_ls = [], param = 'label'):
		const = ''
		if param in cmds_dic[function]:
			const = cmds_dic[function][param]
		else:
			if param in baseparam_ls:
				key_index = baseparam_ls.index(param)
				key = '<key{}>'.format(str(key_index))
				if key in cmds_dic[function]:
					const = cmds_dic[function][key]
		return const
	def response_eew(self, csv, standard = 0):
		eew = csv.split(',')
		eew_dic = {}
		if 'eew' in csv:
			eew_dic['title'] = '【(｡╹ω╹｡)実験中(｡╹ω╹｡)'
		elif eew[1] != '01':
			eew_dic['title'] = '【緊急地震速報'
		else:
			eew_dic['title'] = '[訓練]【緊急地震速報'
		eew_dic['date'] = eew[2]
		if eew[5] in self.eew_ids_set:
			if eew[3] in {'8', '9'}:
				eew_dic['title'] = ''.join(['[最終]', eew_dic['title']])
				self.eew_ids_set.remove(eew[5])
			else:
				return ''
		else:
			self.eew_ids_set.add(eew[5])
		eew_dic['time'] = eew[6].split(' ')[1]
		eew_dic['area'] = eew[9]
		eew_dic['depth'] = ''.join([eew[10], 'km'])
		eew_dic['magnitude'] = eew[11]
		eew_dic['seismic_intensity'] = eew[12]
		if eew[13] == '1':
			eew_dic['eqType'] = '海洋'
		else:
			eew_dic['eqType'] = '内陸'
		eew_dic['alert'] = eew[14]
		eew_alert = ''
		if eew[0] != '35':
			eew_alert = ''.join([eew_dic['title'], '<震度', eew_dic['seismic_intensity'], '> M', eew_dic['magnitude'], '】\n震源:', eew_dic['area'], ' (', eew_dic['eqType'], ')\n', eew_dic['time'], '発生', ' 深さ', eew_dic['depth']])
		else:
			eew_alert = ''.join([eew_dic['title'], '<震度', eew_dic['seismic_intensity'], '>】\n震源:', eew_dic['area'], ' (', eew_dic['eqType'], ')\n', eew_dic['time'], '発生', '深さ', eew_dic['depth']])
		return eew_alert
	def monitor_timeline(self, status):
		ans = ''
		text = status['clean_text']
		screen_name = status['user']['screen_name']
		filename = ''
		if status['user']['screen_name'] == 'eewbot':
			screen_name = ''
			ans = self.response_eew(csv = text, standard = 0)
		elif 'LiveAI_' in screen_name:
			return False
		elif self.stats.tweet_cnt_hour > 100:
			return False
		elif status['entities']['urls']:
			return False
		elif status['user']['screen_name'] in self.bots_set:
			return False
		elif '#とは' in status['text']:
			word = text.replace('#とは', '').replace(' ', '')
			ans = crawling.search_wiki(word = word)
			if 'に一致する語は見つかりませんでした' in ans and not self.bot_id in status['text']:
				ans = ''
			else:
				while len(ans) > 130:
					ans = '。'.join(ans.split('。')[:-2])
				ans = ''.join([ans, '。'])
		elif '#makeQR' in status['text']:
			qrdata = status['text'].replace('@'+ self.bot_id, '').replace('#makeQR', '')
			filename = opencv_functions.make_qrcode(data = qrdata)
			if filename:
				ans = 'QR-Codeをつくりました。'
			else:
				ans = 'QR-Code作成に失敗'
		elif 'add' in text:
			return False
		elif is_kusoripu(text):
			operate_sql.save_phrase(phrase = text, author = screen_name, status = 'kusoripu', character = 'sys', s_type = 'AutoLearn')
			rand = np.random.rand()
			if rand < 0.08:
				ans = get_kusoripu(tg1 = screen_name)
				screen_name = ''
		elif text in set(self.twlog_pool.timeline_twlog[:5]):
			ans = ''.join(['\n', text,'(パクツイ便乗)'])
			if len(''.join([ans,'@',screen_name, ' '])) > 140:
				ans = text
		elif 'respon' in text:
			return False
		elif status['in_reply_to_screen_name'] in {None, self.bot_id}:
			special_response_word = _.crowlList(text = text, dic = self.tmp.response)
			if special_response_word:
				ans = operate_sql.get_phrase(status =  special_response_word, character= self.default_character)
			else:
				text = _.clean_text2(text)
				mas = natural_language_processing.MA.get_mecab_ls(text)
				ans = dialog_generator.extract_haiku(mas)
		#ツイート
		if ans:
			try:
				if screen_name:
					userinfo, is_new_user = operate_sql.read_userinfo(screen_name)
					p(userinfo)
					if not 'select_chara' in userinfo:
						userinfo['select_chara'] = self.default_character
					if userinfo['select_chara'] != self.default_character:
						return False
				return self.send(ans, screen_name = screen_name, status_id = status['id_str'], imgfile = filename, mode = 'tweet')
			except Exception as e:
				logger.debug(e)
				return False
		else:
			return False
	def get_deltasec(self, time_future, time_past):
	#time_future - time_past時間計測(秒)
		try:
			try:
				delta = time_future - time_past
			except: #文字列対策
				logger.debug('convert str into datetime')
				delta = time_future - datetime.strptime(time_past, '%Y-%m-%d %H:%M:%S.%f')
			deltasec = delta.total_seconds()
			return deltasec
		except Exception as e:
			logger.debug(e)
			deltasec = 50
			return deltasec
	def _convert_first_personal_pronoun(self, word, convert_word):
		if word in {'私', 'わたし', 'ぼく', '僕', 'あたし', 'おれ', '俺', 'オレ', '拙者', 'わし'}:
			return convert_word
		else:
			return word
	#MAIN FUNCTION
	def main(self, status, mode = 'dm', userinfo = '', is_new_user = False):
		ans = ''
		IMGfile = ''
		tweet_status = ''
		filename = ''
		delay_sec = 0
		text = status['clean_text']
		status_id = status['id_str']
		screen_name = status['user']['screen_name']
		bot_id = self.bot_id
		if not userinfo:
			userinfo, is_new_user = operate_sql.read_userinfo(screen_name)
		self.sync_now()
		if not 'select_chara' in userinfo:
			userinfo['select_chara'] = self.default_character
		if not userinfo['select_chara']:
			userinfo['select_chara'] = self.default_character
		userinfo['context'] = text
		call_chara_ls = iscalledBOT(text = text,  select_set = {self.default_character})
		if not call_chara_ls:
			pass
		elif any([call_phrase in text for call_phrase in {'おいで', 'かもん', 'hey', 'きて', 'こい', '来', '114514'}]):
			new_chara = call_chara_ls[0]
			if new_chara != userinfo['select_chara']:
				ans = ''.join([userinfo['select_chara'],'→', new_chara, '「', operate_sql.get_phrase(status = 'よびだし', character = new_chara), '」'])
				userinfo['select_chara'] = new_chara
			else:
				ans = ''.join([userinfo['select_chara'],'「', operate_sql.get_phrase(status = 'よびだし', character = userinfo['select_chara']), '」'])
			try:
				filename = _.getRandIMG(DATADIR + '/imgs/' + new_chara)
			except:
				filename = ''
		# character = userinfo['select_chara']
		character = self.default_character
		deltasec = self.get_deltasec(time_future = self.now, time_past = userinfo['time'])

		#返答タイムアウト処理
		if deltasec > 1000:
			userinfo['cnt'] = 0
			userinfo['context'] = ''
			userinfo['mode'] = 'dialog'
			userinfo['select_chara'] = self.default_character
		dialog_obj = dialog_generator.DialogObject(status['text'].replace(self.atmarked_bot_id, ''))
		nlp_summary = dialog_obj.nlp_data.summary
		# p(nlp_summary)
		acceptability = np.random.rand()
		# if not nlp_summary.delay_sec is None:
			# delay_sec = nlp_summary.delay_sec
		if not self.bot_id in status['text']:
			pass
		# 応答
		elif 'ping' in text:
			ans = ''.join(['Δsec : ', str(deltasec)])
		# elif 'userinfo' in cmds_dic:
		# 	ans = str(userinfo)
		# elif 'system' in cmds_dic:
		# 	if 'default' in cmds_dic['system']['<key0>']:
		# 		userinfo['mode'] = 'dialog'
		# 		userinfo['select_chara'] = 'sys'
		# 		screen_name = self.manager_id
		# 		ans = 'system log]\n --force, @' + screen_name+ '\'s mode -> default...'
		elif userinfo['mode'] == 'ignore':
			if 'ごめん' in text:
				userinfo['cnt'] = 0
				userinfo['mode'] = 'dialog'
				ans = operate_sql.get_phrase(status = 'ゆるす', n = 20, character = character)
			else:
				userinfo['cnt'] = 0
				userinfo['mode'] = 'dialog'
		elif deltasec < 3 and not is_new_user:
			ans = operate_sql.get_phrase(status =  'tooFreq', n = 20, character = character)
			userinfo['mode'] = 'ignore'
		elif userinfo['mode'] == 'add.text':
			if status['in_reply_to_screen_name'] in {self.bot_id}:
				text = status['text'].replace(self.atmarked_bot_id, '')
				if 'end' in text:
					userinfo['mode'] = 'dialog'
					userinfo['tmp'] = ''
					ans = '[学習モード]をクローズしました。この結果は開発にフィードバックされます。ご協力感謝します。'
				elif 'ttp' in text:
					if screen_name != self.manager_id:
						ans = '画像やURLを覚えさせるためには、管理者権限が必要です。'
				if not ans:
					text = re.sub(r'(@[^\s　]+)', '{ID}', text)
					labelstatus = userinfo['tmp']
					if '</>' in labelstatus:
						character, labelstatus = labelstatus.split('</>')
					userinfo['cnt'] = 0
					operate_sql.save_phrase(phrase = text, author = screen_name, status = labelstatus, character = character,s_type = 'UserLearn')
					ans = ''.join(['[学習モード] ', labelstatus, ' of ', character, ' SAVED!!...\n 続けて覚えさせるテキストをリプライしてください。\n\'end\'と入力するまでモードは続きます。'])
			else:
				ans = '[学習モード]の途中です。覚えさせるテキストをリプライしてください。\n\'end\'と入力するまでモードは続きます。'
		elif userinfo['mode'] == 'kadai':
			if status['in_reply_to_screen_name'] in {self.bot_id}:
				text = status['text'].replace(self.atmarked_bot_id, '')
				text = re.sub(r'(@[^\s　]+)', '{ID}', text)
				if 'end' in text:
					userinfo['mode'] = 'dialog'
					userinfo['tmp'] = ''
					ans = '[課題モード]CLOSED!!...\nこの結果は開発にフィードバックされます。ご協力感謝します。\n報酬として50EXP獲得\n[現在:'+ str(userinfo['exp']) +'EXP]'
					userinfo['exp'] += 50
				else:
					labelstatus = userinfo['tmp']
					userinfo['cnt'] = 0
					operate_sql.save_phrase(phrase = text, author = screen_name, status = labelstatus, character = 'sys',s_type = 'kadai.annotate')
					userinfo['tmp'] = np.random.choice(['好評', '苦情', '要望', '質問'])
					userinfo['exp'] += 100
					ans = '[課題モード] SAVED!!...報酬として100EXP獲得。\n[現在:'+ str(userinfo['exp']) +'EXP]\n 次は「'+ userinfo['tmp'] + '」のテキストをリプライしてください。e.g.) 好評 -> いいですねー\n\'end\'と入力するまでモードは続きます。'
			else:
				ans = '[課題モード]の途中です。\n\'end\'と入力するまでモードは続きます。'
		elif nlp_summary.has_function('禁止') and nlp_summary.value:
			if nlp_summary.dativ:
				if nlp_summary.akkusativ:
					ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.dativ, 'に', nlp_summary.akkusativ, 'を', nlp_summary.value + 'しないであげます。'])
				else:
					ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.dativ, 'に', nlp_summary.value + 'しないであげます。'])
			elif nlp_summary.akkusativ:
				ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.akkusativ, 'を', nlp_summary.value + 'しないであげます。'])
		elif nlp_summary.value in {'作る', 'つくる', '作成する'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				if nlp_summary.akkusativ in {'QR'}:
					qrdata = status['text'].replace(self.atmarked_bot_id, '').replace('#makeQR', '')
					filename = opencv_functions.make_qrcode(data = qrdata)
					if filename:
						ans = 'QR-Codeをつくりました。'
					else:
						ans = 'QR-Code作成に失敗'
				else:
					ans = 'えっと。。QRだけしか今は作れないです。何をつくればいいですか？'
			# elif '検索して' in text:
			# 	word = natural_language_processing.MA.get_mecab(text.replace('検索して', ''), mode = 7, form = ['名詞'])[0]
			# 	ans = crawling.search_weblioEJJE(word = word)
		elif nlp_summary.value in {'覚える', '記憶する', '学習する', 'おぼえる'}:
			is_accepted = False
			if nlp_summary.has_function('要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				userinfo['mode'] = 'add.text'
				# cmds = text.split(' ')
				tmplabel = nlp_summary.akkusativ
				try:
					chara = cmds[2]
				except:
					chara = character
				userinfo['tmp'] = '</>'.join([chara, tmplabel])
				userinfo['cnt'] = 0
				ans = '[学習モード]\n' +chara +'に「' + tmplabel+ '」として覚えさせるテキストをリプライしてください。\nendと入力するまでモードは続きます。'
		elif nlp_summary.value in {'勧誘する'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				cmds = text.split(' ')
				picDIR = DATADIR + '/imgs/ガチャ'
				if userinfo['exp'] < 0:
					userinfo['exp'] = 0
					ans = operate_sql.get_phrase(status =  '勧誘チケ.shortexp', character = character)
				elif userinfo['exp'] < 500:
					ans = operate_sql.get_phrase(status =  '勧誘チケ.shortexp', character = character)
				else:
					try:
						filename = _.getRandIMG(picDIR)
						userinfo['exp'] -= 500
						ans = operate_sql.get_phrase(status =  '勧誘チケ.success', character = character) + ' EXP -500'
					except:
						ans = operate_sql.get_phrase(status =  '勧誘チケ.error', character = character)
		# elif 'NG' in text:
		# 	try:
		# 		cmds = text.split(' ')
		# 		tag = cmds[1]
		# 		if operate_sql.evalPhrase(phrase = tag, ok_add = 0, ng_add = 1):
		# 			ans = operate_sql.get_phrase(status =  'reportNG.success', character = character)
		# 		else:
		# 			ans = operate_sql.get_phrase(status =  'reportNG.false', character = character)
		# 	except:
		# 		ans = operate_sql.get_phrase(status =  'reportNG.error', character = character)
		elif 'media' in status['entities'] and status['in_reply_to_screen_name'] in {self.bot_id}:
			userinfo['cnt'] = 0
			fileID = self.now.strftime('%Y%m%d%H%M%S')
			if 'update' in text:
				if 'icon' in text:
					self.bot_profile.abs_icon_filename = _.saveImg(media_url = status['extended_entities']['media'][0]['media_url'].replace('_normal', ''), DIR = ''.join([DIRusers,'/',self.bot_id]), filename = '_'.join([screen_name, fileID, 'icon.jpg']))
					ans = operate_sql.get_phrase(status =  'update.icon.success', character = character)
				elif 'banner' in text:
					self.bot_profile.abs_banner_filename =  _.saveImg(media_url = status['extended_entities']['media'][0]['media_url'].replace('_normal', ''), DIR = ''.join([DIRusers,'/',self.bot_id]), filename = '_'.join([screen_name, fileID, 'banner.jpg']))
					ans = operate_sql.get_phrase(status =  'update.icon.banner', character = character)
				if screen_name == '_mmKm':
					self.bot_profile.save()
				else:
					set_time = self.now + timedelta(hours=0, minutes=10)
					operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'default', 'to_whom': screen_name, 'when':set_time, 'tmptext': ''})
					ans = '10分間変更！！'
				self.default_profile()
			elif status['entities']['hashtags']:
				imgtag = status['entities']['hashtags'][0]['text']
				try:
					filenames = _.saveMedias(status, ID = fileID, DIR = '/'.join([DIRIMGfeedback, imgtag]))
					ans = operate_sql.get_phrase(status =  'appreciate.giveme.img', character = character).format(imgtag)
				except Exception as e:
					logger.debug(e)
					ans = operate_sql.get_phrase(status =  'err.get.img', character = character)
			else:
				try:
					filenames = _.saveMedias(status, ID = fileID, DIR = DIRIMGtmp)
					filename = filenames[0]
					label = ''
					pic = opencv_functions.read_img(filename)
					is_bar_detected, zbarans = opencv_functions.passzbar(pic)
					if is_bar_detected:
						img_kind = zbarans[0].decode('utf-8')
						zbarans = zbarans[1].decode('utf-8')
					else:
						label, img_kind, IMGfile = machine_learning_img.predictSVM(filename  = filename, isShow = False, model = modelSVM, workDIR = '')
					if img_kind in {'QR-Code'}:
						ans = zbarans
						filename = ''
					elif img_kind == 'anime':
						ans = operate_sql.get_phrase(status =  'confirm.detect.img', character = character).format(label)

						drc = '/'.join([DIRIMGfeedback, label])
						if os.path.exists(drc) == False:
							os.mkdir(drc)
						shutil.copy(filename, drc)
						userinfo['mode'] = 'confirm.tag.img'
						logger.debug('/'.join([drc, filename.split('/')[-1]]))
						userinfo['tmpFile'] = '/'.join(rc, filename.split('/')[-1])
						filename = IMGfile
					elif img_kind == 'cat':
						ans = operate_sql.get_phrase(status =  'detect_cat', character = character)
						filename = IMGfile
					else:
						ans = operate_sql.get_phrase(status =  'confirm.detect.img.noface', character = character).format(label)
						filename = ''
						userinfo['mode'] = 'dialog'

				except Exception as e:
					logger.debug(e)
					ans = operate_sql.get_phrase(status =  'err.get.img', character = character)

		elif userinfo['cnt'] > 6:
			ans = operate_sql.get_phrase(status =  'cntOver', n = 20, character = character)
			userinfo['mode'] = 'ignore'

		# elif 'img' in cmds_dic:
		# 	cmds = text.split(' ')
		# 	kind = cmds[1]
		# 	umipicDIR = '/Users/masaMikam/Dropbox/Project/IAs/Data/imgs/'+ kind
		# 	try:
		# 		filename = _.getRandIMG(umipicDIR)
		# 		ans = '...'
		# 	except:
		# 		ans = '...none'
		# elif 'giveme' in cmds_dic:
		# 	add_exp = np.random.rand() * 100
		# 	userinfo['exp'] += add_exp
		# 	userinfo['tmpTime. = self.now
		# 	ans = '{add_exp}EXP GET!!\nTotal: {total_exp}EXP'.format(add_exp == str(add_exp), total_exp = str(userinfo['exp']))
		# elif 'send' in cmds_dic:
		# 	try:
		# 		cmds = status['text'].replace(''.join(['@', bot_id, ' ']), '').split(' ')
		# 		tgname = cmds[1].replace('@', '')
		# 		tag = cmds[2]
		# 		user = self.twf.get_userinfo(screen_name = tgname)
		# 		is_following = user['following']
		# 		if is_following:
		# 			ans = operate_sql.get_phrase(status =  tag, character = character)
		# 			if '...:[' in ans:
		# 				ans = operate_sql.get_phrase(status =  'nodata', character = character)
		# 			else:
		# 				screen_name = tgname
		# 				status_id = ''
		# 		else:
		# 			ans = operate_sql.get_phrase(status =  'send.notFF', character = character)
		# 	except:
		# 		ans = operate_sql.get_phrase(status =  'send.error', character = character)
		# elif call_chara_ls and 'hey' in text:
		# 	if text == 'hey':
		# 		ans = '現在は、' + userinfo['select_chara']+ '。\nhey ○○\nで変更可能キャラは...\n' + str(self.tmp.charas.list)
		# 	try:
		# 		cmds = text.split(' ')
		# 		newchara = cmds[1]
		# 		if newchara in chara_set:
		# 			userinfo['select_chara'] = newchara
		# 			ans = '「' + character + '」=>「' + newchara + '」\n'
		# 			ans += operate_sql.get_phrase(status =  'よびだし', character = newchara)
		# 			try:
		# 				filename = _.getRandIMG(DATADIR + '/imgs/' + newchara)
		# 			except:
		# 				filename = ''
		# 		else:
		# 			ans = 'Only ' + str(charaSet)
		# 	except:
		# 		ans = operate_sql.get_phrase(status =  'hey.error', character = character)

		# elif 'check' in cmds_dic:
		# 	target = self.construct_func(cmds_dic, function = 'kusoripu', baseparam_ls = ['target', 'delay'], param = 'target')
		# 	if target == 'response':
		# 		ans = str(self.tmp.response)
		# 	else:
		# 		ans = ''
		# elif 'resp' in cmds_dic:
		# 	try:
		# 		cmds = text.split(' ')
		# 		tgword = cmds[1]
		# 		response = ''.join(cmds[2:])
		# 		logger.debug(response)
		# 		if len(tgword) > 3:
		# 			# tmp['responseWord.gwor = response
		# 			if operate_sql.save_phrase(phrase = response, author = screen_name, status = tgword, s_type = 'response'):
		# 				if tgword in self.tmp.response:
		# 					ans = 'SAVED]...' + response
		# 				else:
		# 					self.tmp.response.append(tgword)
		# 					ans = 'TL上の「' + tgword + '」をモニタリングして10分間反応します。\n 反応文を追加するには半角スペース区切りで\n response ' + tgword + ' [反応文]'
		# 					set_time = self.now + timedelta(hours=0, minutes=10)
		# 					operate_sql.save_task(taskdict = {'who':screen_name, 'what': 'del.response', 'to_whom': screen_name, 'when':set_time, 'tmptext': tgword})
		# 			else:
		# 				ans = 'セー
		# 		else:
		# 			ans = '監視ワードは4文字以上である必要があります。'
		# 	except:
		# 		ans = '設定失敗。半角スペースで区切ってオーダーしてください。'
		elif nlp_summary.value in {'呼ぶ','よぶ', '呼び出す','よびだす', '呼び出しする', '出す'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				if nlp_summary.akkusativ is None:
					ans = 'えっと...だれを呼び出すのですか？'
				else:
					target_name = nlp_summary.akkusativ
					try:
						# self.twf.give_fav(status_id)
						# TODO] Dicをつくるべし。
						if target_name in {'海未', 'うみちゃん', 'うむちゃん'}:
							ans = '@LiveAI_Umi'
						elif target_name in {'穂乃果'}:
							ans = '@LiveAI_Honoka'
						elif target_name in {'絵里'}:
							ans = '@LiveAI_Eli'
						elif target_name in {'花陽', 'かよちん'}:
							ans = '@LiveAI_Hanayo'
						elif target_name in {'真姫'}:
							ans = '@LiveAI_Maki'
						elif target_name in {'凛', '凛ちゃん'}:
							ans = '@LiveAI_Rin'
						elif target_name in {'ちゃんあ'}:
							ans = '@chana1031'
						elif target_name in {'ポケ海未'}:
							ans = '@umi0315_pokemon'
						else:
							ans = ''.join([nlp_summary.akkusativ, 'は呼び出しできません。'])
					except Exception as e:
						logger.debug(e)
						ans = 'よびだし失敗。管理者にお問い合わせください。'
					else:
						ans = ''.join([nlp_summary.akkusativ, 'は呼び出しできません。'])

		elif nlp_summary.value in {'送る','送れる', '送信する', 'クソリプ送信する', 'kusoripu送信する','爆撃する'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				nlp_summary.dativ = self._convert_first_personal_pronoun(word = nlp_summary.dativ, convert_word = screen_name)
				if nlp_summary.value in {'クソリプ送信する', 'kusoripu送信する'}:
					nlp_summary.akkusativ  = 'クソリプ'
				if nlp_summary.akkusativ is None:
					ans = 'えっと...何を送信するのですか？'
				elif nlp_summary.dativ is None:
					ans = ''.join(['えっと...誰に', nlp_summary.akkusativ, 'を送信するのですか？'])
				else:
					target_name = nlp_summary.dativ
					user = self.twf.get_userinfo(screen_name = target_name)
					if not user['following']:
						ans = 'そのユーザーはFF外です。送信はできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
					elif nlp_summary.akkusativ in {'kusoripu', 'クソリプ'}:
						try:
							self.twf.give_fav(status_id)
							screen_name = ''
							status_id = ''
							ans = get_kusoripu(tg1 = target_name)
						except Exception as e:
							logger.debug(e)
							ans = 'クソリプ失敗。管理者にお問い合わせください。'
					else:
						ans = ''.join([nlp_summary.akkusativ, 'は送信できません。'])

		elif nlp_summary.value in {'戻る','もどる', 'なおる', '直る'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				if nlp_summary.dativ is None:
					ans = ''.join(['えっと...なにに戻ってほしいのですか？'])
				elif nlp_summary.dativ in {'デフォルト', '元', '元通り'}:
					if self.default_profile():
						ans = 'デフォルトに戻りました'
						self.tmp.imitating = self.bot_id
					else:
						ans = 'デフォルトに戻るのに失敗 @_apkX'
		elif nlp_summary.value in {'再起動する'}:
			if screen_name != self.manager_id:
				ans = '管理者権限なし'
			else:
				ans = 'restarting system... wait 60sec'
				set_time = self.now + timedelta(hours=0, seconds=60)
				operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'restart_program', 'to_whom': screen_name, 'when':set_time, 'tmptext': ''})
		elif nlp_summary.value in {'まねる', 'モノマネする'}:
			is_accepted = False
			if nlp_summary.has_function('希望', '要望'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				nlp_summary.akkusativ = self._convert_first_personal_pronoun(word = nlp_summary.akkusativ, convert_word = screen_name)
				target_name = nlp_summary.akkusativ
				if not target_name:
					target_name = nlp_summary.dativ
				if not target_name:
					ans = 'えっと...誰をまねるのですか？'
				else:
					user = self.twf.get_userinfo(screen_name = target_name)
					if not user['following']:
						ans = 'そのユーザーはFF外です。ものまねできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
					else:
						try:
							if self.twf.imitate(target_name):
								ans = operate_sql.get_phrase(status =  'imitate.success', character = character).format(''.join(['@', target_name, ' ']))
								mode = 'open'
								self.tmp.imitating = target_name
								set_time = self.now + timedelta(hours=0, minutes=10)
								operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'default', 'to_whom':screen_name, 'when':set_time, 'tmptext': ''})
							else:
								ans = operate_sql.get_phrase(status =  'imitate.error.notFF', character = character).format(''.join(['@', target_name, ' ']))
						except Exception as e:
							logger.debug(e)
							ans = 'クソリプ失敗。管理者にお問い合わせください。'
		elif nlp_summary.value in {'遊ぶ', '尻取りする'} or userinfo['mode'] == 'srtr':
			is_accepted = False
			if userinfo['mode'] == 'srtr':
				is_accepted = True
			if nlp_summary.has_function('希望', '要望', '勧誘'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				if nlp_summary.value in {'尻取りする'} or nlp_summary.dativ in {'尻取り', None} or userinfo['mode'] == 'srtr':
					userinfo['mode'] = 'srtr'
					ans = game_functions.SRTR(text, screen_name)
					if '\END' in ans:
						ans = ans.replace('\END', '')
						userinfo['mode'] = 'dialog'
					if '\MISS' in ans:
						ans = ans.replace('\MISS', '')
						if userinfo['cnt'] > 3:
							ans = operate_sql.get_phrase(status =  'shiritori.end', character = character)
							userinfo['mode'] = 'dialog'
							userinfo['cnt'] = 0
					else:
						userinfo['cnt'] = 0
		elif nlp_summary.value in {'戦う', '対戦する', '倒す', 'たたかう', '申し込む'} or userinfo['mode'] in {'mon', 'battle_game'}:
			is_accepted = False
			if userinfo['mode']  in {'srtr'}:
				is_accepted = True
			if nlp_summary.has_function('希望', '要望', '勧誘'):
				is_accepted = True
			if nlp_summary.has_function('命令'):
				if acceptability < 0.2:
					is_accepted = True
			if not is_accepted:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
			else:
				try:
					if userinfo['mode'] in {'mon', 'battle_game'}:
						enemy_name = None
					else:
						enemy_name = nlp_summary.dativ
					if not enemy_name:
						enemy_name = nlp_summary.akkusativ
					else:
						userinfo['mode'] = 'battle_game'
						intext = status['text'].replace(''.join(['@', self.bot_id, ' ']), '').replace('@', '')
						battle_game = game_functions.BattleGame(screen_name, enemy_name)
						ans = '\n' + battle_game.main(intext)
						userinfo['cnt'] = 0
						if '#END' in ans:
							ans = ans.replace('#END', '')
							userinfo['mode'] = 'dialog'
						if '#MISS' in ans:
							ans = ans.replace('#MISS', '')
						if '#exp' in ans:
							ans, exp = ans.split('#exp')
							userinfo['exp'] += 20
				except Exception as e:
					p(e)
					ans = '工事中...'
					userinfo['mode'] = 'dialog'
		#----------------
		# Feedback_cooperation_program
		elif nlp_summary.value in {'お手伝いする', 'てつだう', '手伝う'}:
			if nlp_summary.has_function('希望'):
				label = np.random.choice(['好評', '苦情', '要望', '質問'])
				ans = operate_sql.get_phrase(status =  'kadai.labeling.text', n = 20, character = character).format(label)
				userinfo['mode'] = 'kadai'
				userinfo['tmp'] = label
			if nlp_summary.has_function('要望'):
				is_following = True
				nlp_summary.akkusativ = self._convert_first_personal_pronoun(word = nlp_summary.akkusativ, convert_word = screen_name)
				if nlp_summary.akkusativ is None:
					target_name = screen_name
				else:
					target_name = nlp_summary.akkusativ
					user = self.twf.get_userinfo(screen_name = tgname)
					is_following = user['following']
				if is_following:
					screen_name = target_name
					status_id = ''
					ans = operate_sql.get_phrase(status =  'haken', character = character)
				else:
					ans = 'そのユーザーはFF外です。お手伝いできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
		#----------------
		# Teach
		elif nlp_summary.value in {'教える'}:
			if nlp_summary.has_function('希望', '要望'):
				if nlp_summary.akkusativ in {'トレンド', '流行語'}:
					ans = '\n- '.join(['[現在のトレンドワード]']+self.tmp.trendwords_ls[:10])
				elif nlp_summary.akkusativ in {'経験値', 'exp', 'EXP', 'Exp'}:
					ans = '\n'.join(['[現在の経験値]:', str(userinfo['exp'])])
		#----------------
		# Omikuji
		elif nlp_summary.value in {'御籤する', '占う'}:
			if nlp_summary.has_function('希望', '要望', '勧誘'):
				ans = operate_sql.get_phrase(status =  'おみくじ', n = 20, character = character)
		#----------------
		# Initialize_tasks
		elif nlp_summary.value in {'初期化する'}:
			if nlp_summary.has_function('命令'):
				self.initialize_tasks()
				ans = 'initialized all tasks...'
		#----------------
		# Followback
		elif nlp_summary.value in {'フォロバする'}:
			if nlp_summary.has_function('希望', '要望', '勧誘'):
				user = self.twf.get_userinfo(screen_name = screen_name)
				is_following = user['following']
				if not is_following:
					try:
						self.twf.is_create_friendship_success(screen_name)
						ans = operate_sql.get_phrase(status =  'followback.success', character = character)
					except:
						ans = operate_sql.get_phrase(status =  'followback.error', character = character)
				else:
					ans = operate_sql.get_phrase(status =  'followback.already', character = character)
		##############
		# Rest Functions
		##############
		elif nlp_summary.has_function('要望', '希望', '勧誘'):
			if acceptability < 0.7:
				ans = operate_sql.get_phrase(status =  'ok', character = character)
			else:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
		elif nlp_summary.has_function('命令'):
			if acceptability < 0.2:
				ans = operate_sql.get_phrase(status =  'ok', character = character)
			else:
				ans = operate_sql.get_phrase(status =  'reject', character = character)
		elif nlp_summary.has_function('疑問'):
			if dialog_obj.is_fact():
				ans = operate_sql.get_phrase(status =  'yes', character = character)
			else:
				ans = operate_sql.get_phrase(status =  'no', character = character)
		else:
			if nlp_summary.entity:
				if acceptability < 0.8:
					if nlp_summary.entity:
						ans = ''.join([nlp_summary.entity, 'は', nlp_summary.value, '...覚えましたし'])
					else:
						ans = ''.join(['なにが', nlp_summary.value, '...???'])
		if not ans:
			ans = dialog_obj.dialog()
			ans = self.convert_text_as_character(ans).replace('<人名>', status['user']['name']).replace(''.join(['@', self.bot_id]), '')
			if not ans:
				ans = '...?'
		if is_new_user:
			p('detected_new_user')
			user = self.twf.get_userinfo(screen_name = screen_name)
			is_following = user['following']
			if not is_following:
				welcomeans = operate_sql.get_phrase(status =  'welcomeNewUser', character = character)
				try:
					self.twf.is_create_friendship_success(screen_name)
				except:
					welcomeans = operate_sql.get_phrase(status =  'followback.error', character = character)
			else:
				welcomeans = operate_sql.get_phrase(status =  'welcome.NEWscreen_name', character = character)
			self.send(welcomeans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = mode)

		if ans:
			if delay_sec > 0:
				set_time = self.get_time(hours = 0, seconds =  delay_sec, is_noised = True)
				operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': 'tweet', 'to_whom': screen_name, 'when':set_time, 'tmpid': status_id, 'tmptext': ans})
			else:
				tweet_status = self.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = mode)
			userinfo['context'] = '</>'.join([userinfo['context'], ans])

		userinfo['time'] = self.now
		try:
			userinfo['cnt'] += 1
		except:
			userinfo['cnt'] = 0
		try:
			userinfo['exp'] += 10
		except:
			userinfo['exp'] = 0
		operate_sql.save_userinfo(userinfo)
		return tweet_status

	def is_not_ignore(self, status):
		try:
			if status['retweeted']:
				return False
			if status['is_quote_status']:
				return False
			screen_name = status['user']['screen_name']
			if any([ng_word in status['text'] for ng_word in ['RT', 'QT', '定期', '【', 'ポストに到達', 'リプライ数']]):
				if screen_name != self.manager_id:
					return False
			if screen_name == self.bot_id:
				return False
			if screen_name in self.response_exception_set:
				return False
			return True
		except Exception as e:
			logger.debug('is_not_ignore')
			logger.debug(e)
			return False

	def is_react(self, status):
		try:
			text = status['clean_text']
			if self.bot_id in status['text']: #リプライ全応答。
				return True
			elif iscalledBOT(text = text,  select_set = {self.default_character}):
				return True
			rand = np.random.rand()
			if status['user']['screen_name'] in self.bots_set:
				if rand < 0.001: #BOTに対する自発。0.1%
					return True
			if status['user']['screen_name'] in self.karamix2_set:
				if rand < 0.02: #2%
					return True
			if rand < 0.01: #自発。0.5%
				return True
			return False
		except Exception as e:
			logger.debug('is_react')
			logger.debug(e)
			return False
	def on_status_main(self, status):
		try:
			# self.sync_json(json = None, is_save = False)
			if self.is_not_ignore(status):
				self.stats.TL_cnt += 1
				status_id = status['id_str']
				screen_name = status['user']['screen_name']
				replyname = status['in_reply_to_screen_name']
				text = _.clean_text(status['text'])
				if not replyname is None:
					p(self.bot_id,':STREAM>>', status['user']['name'], ']@', replyname, text)
				else:
					p(self.bot_id,':STREAM>>', status['user']['name'], ']', text)
				self.sync_now()
				#ツイートステータス情報追加処理
				status['now'] = self.now
				status['clean_text'] = text
				#直近ツイート処理
				if self.monitor_timeline(status):
					return True
				# リアクション
				if self.is_react(status):
					tweet_status = self.main(status, mode = 'tweet')
				# 記憶部
				if not text in set(self.twlog_pool.timeline_twlog):
					try:
						operate_sql.save_tweet_status(status)
					except:
						pass
				#Tweetプーリング
					if not screen_name in self.bots_set:
						if not status['entities']['urls']:
							if len(text) > 5:
								if not any([ng_word in text for ng_word in ['便乗', 'imitate', 'learn', 'img', 'kusoripu', 'haken', 'add', '午̷̖̺͈̆͛͝前̧̢̖̫̊3̘̦時̗͡の̶̛̘̙̤̙̌̉͢い̷゙̊̈̓̓̅ば̬̬̩͈̊͡ら゙̜̩̹ぎ̫̺̓ͣ̕͡げ̧̛̩̞̽ん゙̨̼̗̤̂̄']]):
									self.twlog_pool.append_and_adjust_timeline_twlog(text)
				if not screen_name in {self.bot_id}:
					if not status['in_reply_to_status_id_str'] is None:
						try:
							operate_sql.save_tweet_dialog(status)
						except:
							pass
			# self.sync_json()
			return True
		except Exception as e:
			logger.debug(e)
			logger.debug('+++++timeline_status+++++++')
			return True
	def on_direct_message_main(self, status):
		try:
			# self.sync_json(is_save = False)
			self.stats.DM_cnt += 1
			# status = status._json
			status = self.twf.convert_direct_message_to_tweet_status(status)
			operate_sql.save_tweet_status(status, self.tmp)
			if self.is_not_ignore(status):
				try:
					text = _.clean_text(status['text'])
					status['clean_text'] = text
					self.sync_now()
					#ツイートステータス情報追加処理
					status['now'] = self.now
					status['clean_text'] = text
					screen_name = status['user']['screen_name']
					userinfo, is_new_user = operate_sql.read_userinfo(screen_name)
					context = userinfo['context'].split('</>')[-1]
					operate_sql.save_tweet_dialog(status, tmp = self.tmp, logtext = context)
					tweet_status = self.main(status, mode = 'dm', userinfo = userinfo, is_new_user = is_new_user)
				except Exception as e:
					logger.debug(e)
			# self.sync_json()
		except Exception as e:
			logger.debug(e)
			logger.debug('++++direct_message++++++')
		return True

	def on_event_main(self, status):
		p(status['event'])
		p(status)
		try:
			if status['event'] == 'favorite':
				if status['target']['screen_name'] == self.bot_id:
					text = _.clean_text(status['target_object']['text'])
					operate_sql.save_phrase(phrase = text, author = status['source']['name'], status = 'favorite', character = 'sys',s_type = 'favorite')
			elif status['event'] == 'unfollow':
				p('unfollow')
				if status['target']['screen_name'] == self.bot_id:
					screen_name = status['source']['screen_name']
					p(screen_name)
					if self.twf.is_destroy_friendship_success(screen_name = screen_name):
						return True
			elif status['event'] == 'follow':
				if status['target']['screen_name'] == self.bot_id:
					is_followback_ok = True
					if status['source']['lang'] != 'ja':
						return True
					if status['source']['statuses_count'] < 100:
						return True
					if status['source']['favourites_count'] < 20:
						return True
					if status['source']['listed_count'] / status['source']['followers_count'] < 0.02:
						is_followback_ok = False
					ff_rate = status['source']['followers_count'] / status['source']['friends_count']
					if ff_rate < 0.6:
						is_followback_ok = False
					if not is_followback_ok:
						if status['source']['followers_count'] > 2000:
							is_followback_ok = True
					if is_followback_ok:
						screen_name = status['source']['screen_name']
						if self.twf.is_create_friendship_success(screen_name = screen_name):
							return True
			elif status['event'] == 'user_update':
				if status['target']['screen_name'] == self.bot_id:
					if not status['source']['location'] is None:
						if 'まねっこ' in status['source']['location']:
							return True
					self.bot_profile.name = status['source']['name']
					self.bot_profile.description = status['source']['description']
					self.bot_profile.url = status['source']['url']
					self.bot_profile.id_str = status['source']['id_str']
					self.bot_profile.location = status['source']['location']
					self.bot_profile.save()
		except Exception as e:
			logger.debug(e)
			logger.debug('++++event++++++')
		return True

	def implement_tasks(self, task):
		def task_restart(is_noised = True):
			try:
				duration_min = int(task['tmptext'])
				postmin = self.get_time(minutes = duration_min, is_noised = is_noised)
				operate_sql.update_task(who_ls = [self.bot_id], kinds = [task['what']], taskdict = {'status': 'end'})
				operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': task['what'], 'to_whom': '', 'when':postmin, 'tmptext': task['tmptext']})
			except:
				pass
		try:
			ans = ''
			taskid = task['id']
			todo = task['what']
			screen_name = task['to_whom']
			filename = task['tmpfile']
			status_id = task['tmpid']
			set_time = task['when']
			try_cnt = 0
			if todo == 'timer':
				ans = datetime.strftime(set_time, '%m月%d日 %H時%M分%S秒') + 'です。タイマーの時刻を経過しました。\n' + task['tmptext']
			elif todo == 'tweet':
				ans = task['tmptext']
				try_cnt = task['tmpcnt']
			elif todo == 'default':
				if self.default_profile():
					self.tmp.imitating = self.bot_id
					ans = 'デフォルトに戻りました'
				else:
					ans = 'デフォルトに戻るのに失敗 サポートにお問い合わせください。'
			# elif todo == 'teiki':
			# 	ans = operate_sql.get_phrase(status = 'teiki', n = 100, character= self.default_character)
			# 	post20min = self.get_time(minutes = 30)
			# 	operate_sql.update_task(who_ls = [self.bot_id], kinds = [todo], taskdict = {'status': 'end'})
			# 	operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': todo, 'to_whom': '', 'when':post20min})
			elif todo == 'teiki.MC':
				try:
					chara = self.default_character
					ans = dialog_generator.dialog('', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = [], BlackList = self.tmp.feedback_exception, min_similarity = 0.8, character = chara, tools = 'MC')
					ans = ans.replace('<人名>', 'アルパカ')
					task_restart()
				except Exception as e:
					logger.debug(e)

			elif todo == 'teiki.trendword':
				trendwords = self.twf.getTrendwords()
				trendword = np.random.choice(trendwords)
				ans = operate_sql.get_phrase(status = 'トレンドワード', character= self.default_character).format(trendword)
				self.tmp.trendwords_ls = trendwords
				task_restart()

			elif todo == 'update.lists':
				userinfo_me = self.twf.twtr_api.me().__dict__
				bot_id = userinfo_me['screen_name']
				self.bot_id = bot_id
				self.bots_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'BOT'))
				self.karamix2_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'KARAMIx2'))
				self.response_exception_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'responseException'))
				self.feedback_exception_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'feedbackException'))
				task_restart()
			elif todo == 'del.response':
				try:
					self.tmp.response.remove(task['tmptext'])
				except:
					logger.debug('del err')
			elif todo == 'erase.tmp.stats.tweet_cnt_hour':
				self.stats.tweet_cnt_hour = 0
				task_restart()
			elif todo == 'save_stats':
				operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'time_line_cnt', 'number': self.stats.TL_cnt})
				operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'direct_message_cnt', 'number': self.stats.DM_cnt})
				task_restart(is_noised = False)
			elif todo == 'reconnect_wifi':
				_.reconnect_wifi()
				task_restart()
			elif todo == 'reload_modules':
				importlib.reload(natural_language_processing)
				importlib.reload(dialog_generator)
				importlib.reload(game_functions)
				# importlib.reload(twtr_functions)
				task_restart()
			elif todo == 'restart_program':
				print('restrarting_program...')
				_.restart_program()
			elif todo == 'update_userprofile':
				# self.bot_profile = self.twf.twtr_api.me()
				# if not 'まねっこ' in self.bot_profile.location:
				# 	self.bot_profile = self.twf.download_userobject_urls(self.bot_profile, DIR = DIRusers)
				# task_restart()
				pass
			else:
				pass
			#Answer
			if ans:
				self.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = 'tweet', try_cnt = try_cnt)
			operate_sql.update_task(who_ls = [self.bot_id], taskid = taskid, taskdict = {'status': 'end'})
			# self.sync_json(is_save = False)
			return True
		except Exception as e:
			p(task)
			logger.debug(e)
			return True
	def get_time(self, hours = 0, minutes = 5, seconds = 0, is_noised = True):
		if is_noised:
			rand_sec = np.random.randint(0, 60)
		else:
			rand_sec = 0
		seconds += rand_sec
		rand_time = self.now + timedelta(hours = hours, minutes = minutes, seconds = seconds)
		return rand_time
	def initialize_tasks(self):
		operate_sql.update_task(who_ls = [self.bot_id], kinds = ['tweet', 'teiki','teiki.MC', 'teiki.trendword', 'erase.tmp.stats.tweet_cnt_hour', 'update.lists', 'default','update_userprofile','save_stats', 'reconnect_wifi', 'restart_program'], taskdict = {'status': 'end'})
		self.sync_now()
		task_duration_dic = {
			'teiki': 30,
			'teikiMC': 40,
			'teiki.trendword': 30,
			'erase.tmp.stats.tweet_cnt_hour': 60,
			'update.lists': 30,
			'update_userprofile' : 10,
			'save_stats': 20, 
			'restart_program': 60
			}
		if self.bot_id == 'LiveAI_Umi':
			task_duration_dic['reconnect_wifi'] = 3
		def save_task(task_name, duration_min):
			rand_start_min = np.random.randint(0, 20)
			operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': task_name, 'to_whom': '', 'tmptext': str(duration_min), 'when': self.get_time(minutes = rand_start_min)})
		[save_task(task_name, duration_min) for task_name, duration_min in task_duration_dic.items()]
##############
# Main Functions
##############
def task_manager(bot_id, period = 60):
	# twf = twtr_functions.TwtrTools(bot_id)
	time.sleep(5)
	response_funcs = StreamResponseFunctions(bot_id)
	response_funcs.initialize_tasks()
	while True:
		now = response_funcs.sync_now()
		p(bot_id, '_TASK_MANAGER>> ', now)
		tasks = operate_sql.search_tasks(when = now, who = bot_id, n = 10)
		try:
			[response_funcs.implement_tasks(task) for task in tasks if task]
		except Exception as e:
			logger.debug(e)
		time.sleep(period)

def stream(bot_id):
	twf = twtr_functions.TwtrTools(bot_id)
	twf.Stream()
def live_intel(bot_id):
	LiveAI_thread = threading.Thread(target = stream, name = bot_id + '_LiveAI_program', args=(bot_id, ))
	LiveAI_thread.start()
	task_manager_thread = threading.Thread(target = task_manager, name = bot_id + '_task_manager', args=(bot_id, 30, ))
	task_manager_thread.start()
def main(is_experience = True):
	if not is_experience:
		umi_thread = threading.Thread(target = live_intel, name = 'LiveAI_Umi', args=('LiveAI_Umi', ))
		umi_thread.start()
		time.sleep(10)
		honoka_thread = threading.Thread(target = live_intel, name = 'LiveAI_Honoka', args=('LiveAI_Honoka', ))
		honoka_thread.start()
		time.sleep(10)
		rin_thread = threading.Thread(target = live_intel, name = 'LiveAI_Rin', args=('LiveAI_Rin', ))
		rin_thread.start()
		time.sleep(10)
		eli_thread = threading.Thread(target = live_intel, name = 'LiveAI_Eli', args=('LiveAI_Eli', ))
		eli_thread.start()
		time.sleep(10)
		maki_thread = threading.Thread(target = live_intel, name = 'LiveAI_Maki', args=('LiveAI_Maki', ))
		maki_thread.start()
		time.sleep(10)
		hanayo_thread = threading.Thread(target = live_intel, name = 'LiveAI_Hanayo', args=('LiveAI_Hanayo', ))
		hanayo_thread.start()
	else:
		alpaca_thread = threading.Thread(target = live_intel, name = 'LiveAI_Alpaca', args=('LiveAI_Alpaca', ))
		alpaca_thread.start()
if __name__ == '__main__':
	try:
		argvs = sys.argv
		cmd = argvs[2]
	except:
		cmd = 1
	main(is_experience = cmd)









