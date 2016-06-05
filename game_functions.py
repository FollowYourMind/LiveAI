#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
from sql_models import *

# MY PROGRAMs
import natural_language_processing
import _
from _ import p, d, MyObject, MyException
import operate_sql

def Srtr(s = '', user = 'masaMikam', lenrule = 1, cmd = 'normal'):
	if s == '':
		return '( •̀ ᴗ •́ )なにか、言ってくれないとしりとりできないです。\MISS'
	ans = ''
	answord = ''
	wordsList = []
	kanasList = []
	srtrDB = {}
	try:
		# core_sql.create_tables([Srtrtemps], True)
		with core_sql.transaction():
			try:
				srtrdb, created = Srtrtemps.get_or_create(name = user)
				if created == True:
					srtrdb.name = user
					srtrdb.wordsstream = ''
					srtrdb.kanasstream = ''
					srtrdb.lenrule = lenrule
					srtrdb.save()
			except Exception as e:
				print(e)
			core_sql.commit()
	except Exception as e:
		core_sql.rollback()
		print(e)
		wordsList = []
		kanasList = []

	wordsList = srtrdb.wordsstream.split('<JOIN>')
	kanasList = srtrdb.kanasstream.split('<JOIN>')
	try:
		totalcnt = srtrdb.totalcnt
		wincnt = srtrdb.wincnt ## botの勝利数
		losecnt = srtrdb.losecnt ## botの敗北数
	except Exception as e:
		print(e)
		totalcnt = 1
		wincnt = 0
		losecnt = 0
	turncnt = len(wordsList)
	try:
		# アポストロフィに無理やり対応(すごい例外)
		s = s.replace('海未', '[{海未}]')
		if "μ's" in s:
			rawnoun = "μ's"
			kana = 'ミューズ'
		else:
			rawNouns = natural_language_processing.MA.get_mecab(s, form=['名詞'], exception = ['数', '接尾', '非自立', '接続助詞', '格助詞', '代名詞'])
			kanaNouns = natural_language_processing.MA.get_mecab(s, mode = 8, form = ['名詞'], exception = ['数', '接尾', '非自立', '接続助詞', '格助詞', '代名詞'])
			if rawNouns == ():
				ans += '( •̀ ᴗ •́ )名詞の単語が見あたりません。他の単語はありませんか？\MISS'
			rawnoun = rawNouns[0]
			kana = kanaNouns[0]
		p = re.compile("[!-@[-`{-~]")    # 半角記号+半角数字
		cleanednoun = re.sub(p, '', kana)
		gobi = cleanednoun[-1:]
		if gobi == 'ー':
			gobi = cleanednoun.replace('ー','')[-1:]
		gotou = cleanednoun[:1]
		gobi = gobi.replace('ャ','ヤ').replace('ュ','ユ').replace('ョ','ヨ').replace('ッ','ツ').replace('ィ','イ').replace('ァ','ア').replace('ェ','エ').replace('ゥ','ウ').replace('ォ','オ').replace('ヵ','カ').replace('ヶ','ケ').replace('ヮ','ワ')

		word = {}
		lenword = len(kana)
		# try:
		# 	# core_sql.create_tables([Words], True)
		# 	with core_sql.transaction():
		# 		try:
		# 			w, created = Words.create_or_get(word = rawnoun, yomi = kana, head = gotou, tail = gobi, length = lenword)
		# 			if created == False:
		# 				w.word = rawnoun
		# 				w.yomi = kana
		# 				w.head = gotou
		# 				w.tail = gobi
		# 				w.length = lenword
		# 				w.save()
		# 		except Exception as e:
		# 			print(e)
		# 		core_sql.commit()
		# except IntegrityError as ex:
		# 	print (ex)
		# 	core_sql.rollback()
		try:
			lastgobi = kanasList[-1][-1]
			if lastgobi  == 'ー':
				lastgobi  = kanasList[-1].replace('ー','')[-1]
			lastgobi = lastgobi.replace('ャ','ヤ').replace('ュ','ユ').replace('ョ','ヨ').replace('ッ','ツ').replace('ィ','イ').replace('ァ','ア').replace('ェ','エ').replace('ゥ','ウ').replace('ォ','オ').replace('ヵ','カ').replace('ヶ','ケ').replace('ヮ','ワ')
		except Exception as e:
			# print(e)
			lastgobi = ''
		if cmd == 'showlist':
			return wordsList
		elif cmd == 'restart':
			wordsList = []
			kanasList = []
			if lenrule > 1:
				ruleNOTE = 'では、'+ str(lenrule) + '字以上で'
			else:
				ruleNOTE = ''
			if gobi == 'ン':
				rawnoun = 'しりとり'
				gobi = 'リ'
			wordsList.append(rawnoun)
			kanasList.append(kana)
			ans += 'いいですね。'+ruleNOTE+'しりとりしましょう。\nそれでは、「'+rawnoun+'」の「'+gobi+'」から開始です。'
		elif lenword < lenrule and rawnoun != 'しりとり':
				ans += '( •̀ ᴗ •́ )「'+rawnoun+'」ですね。'+ str(lenrule) +'字縛りですから、これでは字数が短いです。\n別の単語はないのですか？「しりとりおわり」で降参してもいいんですよ 〜♪。\MISS'
		else:
			kao = '( •̀ ᴗ •́ )'

		if lastgobi == '':
			wordsList.append(rawnoun)
			kanasList.append(kana)
		if cmd != 'restart':
			ans ='「'+rawnoun+'」ですね。'+gobi+'...\n'
			if lastgobi != gotou:
				ans += '( •̀ ᴗ •́ )その言葉ではだめです。\n' + lastgobi + 'から始まる別の単語でお願いします。「しりとりおわり」で終了してもOKです。\MISS'
			elif rawnoun in wordsList:
				ans += '( •̀ ᴗ •́ )たしか、その言葉は既に使われましたよ。私の勝利ですっ!! \END'
				wordsList = []
				kanasList = []

			elif gobi == 'ン':
				ans += '( •̀ ᴗ •́ )いま、「ン」がつきましたね。私の勝利ですっ!!\END'
				wordsList = []
				kanasList = []

			else:
				wordsList.append(rawnoun)
				kanasList.append(kana)
				LoseFlag = False
				# LoseFLAGについて
				if turncnt > 25:
					LoseFlag = True
				if LoseFlag:
					try:
						with talk_sql.transaction():
							try:
								answords = tfidf.select().where(tfidf.yomi.startswith(gobi), tfidf.yomi.endswith('ン'), tfidf.hinshi << ['名詞', '固有名詞'], ~tfidf.hinshi << ['数']).order_by(tfidf.df.desc()).limit(50)
								answord = choose_answord(answords, word_len_min = lenrule)
							except Exception as e:
								print(e)
								talk_sql.commit()
					except IntegrityError as ex:
						print (ex)
						talk_sql.rollback()
				else:
					try:
						# core_sql.create_tables([Words], True)
						with talk_sql.transaction():
							try:
								answords = tfidf.select().where(tfidf.yomi.startswith(gobi), ~tfidf.yomi.endswith('ン'),  tfidf.yomi != '*', tfidf.hinshi << ['名詞', '固有名詞'], ~tfidf.hinshi2 << ['数', '接尾']).order_by(tfidf.df.desc()).limit(300)
								answord = choose_answord(answords, word_len_min = lenrule)

							except Exception as e:
								print(e)
								talk_sql.commit()
					except IntegrityError as ex:
						print (ex)
						talk_sql.rollback()
				aword = answord.word
				if aword in wordsList:
					wordsList = []
					kanasList = []
					losecnt =+ 1
					ans += aword + ' ですッ!! あ、既に出ていた単語でした...。くっ、私の負けです。\END'
				elif answord.yomi[-1] == 'ン':
					ans += aword + ' ですッ!! あ、「ン」がついてしまいました...。くっ、私の負けです。\END'
				else:
					ansgobi = answord.yomi[-1]
					anskana = answord.yomi
					if ansgobi == 'ー':
						ansgobi = answord.yomi[-2]
						anskana = answord.yomi[:-1]
					wordsList.append(aword)
					kanasList.append(anskana)
					ans += aword + ' ですっ!! 次の頭文字は「' + ansgobi +'」ですよ。'
	except Exception as e:
		print(e)
		ans += '( •̀ ᴗ •́ )思いつきませんでした。悔しいですけど、私の負けです。\END'
		wordsList = []
		kanasList = []
		losecnt =+ 1

	# メモリー
	try:
		# core_sql.create_tables([Words], True)
		with core_sql.transaction():
			try:
				srtrdb = Srtrtemps.get(name = user)
				srtrdb.name = user
				wstream = '<JOIN>'.join(wordsList)
				srtrdb.wordsstream = wstream
				srtrdb.kanasstream = '<JOIN>'.join(kanasList)
				srtrdb.lenrule = lenrule
				srtrdb.save()
			except Exception as e:
				print(e)
			core_sql.commit()
	except IntegrityError as ex:
		print (ex)
		core_sql.rollback()
	return ans
def choose_answord(answords, word_len_min = 3):
	try:
		answord = np.random.choice([w for w in answords])
		if len(answord.yomi) > word_len_min:
			return answord
		else:
			return choose_answord(answords, word_len_min)
	except Exception as e:
		print(e)
		return ''
def SRTR(text, user):
	if 'しりとりおわり' in text:
		with core_sql.transaction():
			try:
				word = Srtrtemps.select().where(Srtrtemps.name == user).limit(1).get()
				word.kanasstream = ''
				word.wordsstream = ''
				word.save()
				core_sql.commit()
				return 'それでは、しりとりは終わりにしましょう。また遊んでくださいね。\END'
			except Exception as e:
				core_sql.rollback()
				return'データの消去に失敗しました。とりあえず、しりとりは終わりにします。\END'
	elif 'しりとり' in text:
		try:
			num = re.match("\d*",cmdlist[1])
			extracted = num.group()
			lenrule = int(extracted)
		except:
			lenrule = 1
		return Srtr(text, user,lenrule,'restart')
	elif text == 'show':
		with talk_sql.transaction():
			wordscnt = tfidf.select().where(tfidf.hinshi << ['名詞', '固有名詞'], tfidf.yomi != '*', ~tfidf.hinshi2 << ['数', '接尾']).count()
			return '現在、SQLに'+ str(wordscnt)+'コの名詞・固有名詞を覚えています。現在の単語の流れ↓\n' + str(Srtr(text, user, 1,'showlist'))
	elif text == 'showlist':
		return Srtr(text, user, 1,'showlist')
	elif text == 'check':
		try:
			checkword = cmdlist[1]
			with core_sql.transaction():
				word = Words.select().where(Words.word == checkword).limit(1).get()
			return checkword + 'の結果...\nよみ:'+ word.yomi+'\n語頭:'+ word.head+'\n語尾:'+ word.tail+'\n長さ:'+ str(word.length)
		except Exception as e:
			core_sql.rollback()
			print(e)
			return 'そのような単語は見当たりません。しりとりに戻りませんか？'
	else:
		return Srtr(text, user)
class CharacterStatus(object):
	def __init__(self, name, character_level = 10):
		self.name = name.replace('@', '')
		self.nickname = self.name[:5]
		self.full_hp = 10
		self.rest_hp = self.full_hp
		self.character_level = character_level
		status = self.read_status(name)
		if status:
			self.character_level = status.character_level
			if status.nickname:
				self.nickname = status.nickname
			self.mode = status.mode
			self.exp = status.exp
			self.exp_to_level_up = status.exp_to_level_up
			self.damage = status.damage
			self.full_hp = status.full_hp
			self.rest_hp = status.rest_hp
			self.hp_gage = status.hp_gage
			self.Atk = status.Atk
			self.Def = status.Def
			self.SpA = status.SpA
			self.SpD = status.SpD
			self.Spe = status.Spe
			self.enemy_name = status.enemy_name
			try:
				self.recalc_status()
			except:
				pass
		else:
			self.character_level = character_level
			self.initialize_status()
		self.level_up_cnt = self.calc_character_level()
		self.praise_flag = False
		self.status = 'normal'
		if self.level_up_cnt > 0:
			self.praise_flag = True
		self.update_hp_gage()
	def read_status(self, user = 'masaMikam'):
		try:
			core_sql.create_tables([CharacterStatusModel], True)
			with core_sql.transaction():
				try:
					status = CharacterStatusModel.select().where(CharacterStatusModel.name == user).get()
					return status
				except Exception as e:
					print(e)
				core_sql.commit()
		except Exception as e:
			core_sql.rollback()
	def recovery_status(self, rate = 1):
		self.damage = 0
		self.rest_hp = self.full_hp * rate
		self.update_hp_gage()
	def initialize_status(self):
		self.mode = 'encount'
		self.status = 'normal'
		self.recalc_status()
		self.recovery_status()
		return True
	def recalc_status(self):
		try:
			userinfo, is_created = operate_sql.get_userinfo(self.name)
			if is_created:
				raise Exception
			if not userinfo['nickname']:
				self.nickname = userinfo['screen_name'].replace('@', '').replace('例外', '')[:5]
			try:
				self.exp = userinfo['exp']
				if not self.exp:
					self.exp = self.character_level ** 3
			except Exception as e:
				print(e)
		except Exception as e:
			p(e)
			self.exp = self.character_level ** 3
		self.total_cnt = 1
		self.last_time = 1
		self.friends_cnt = 100
		self.followers_cnt = 100
		self.statuses_cnt = 100
		self.fav_cnt = 100
		# 計算式
		d = datetime.utcnow() + timedelta(hours = 9)
		now_time = d.strftime("%Y%m%d%H%M%S")
		time_difference = (int(now_time)-int(self.last_time) - 100) // 60
		if not self.character_level:
			status =  self.calc_character_level()
		else:
			self.exp_to_level_up = 0
		# p(self.character_level)
		if self.character_level is None:
			p(self.character_level)
			self.character_level = 10
		self.full_hp = int(np.log2(self.statuses_cnt)*10 * (self.character_level/100) +(self.character_level +10))
		self.Atk = int(np.log2(self.friends_cnt)*10 * (self.character_level/100) +(self.character_level +5))
		self.Def = int(np.log2(self.followers_cnt)*10 * (self.character_level/100) +(self.character_level +5))
		self.SpA = int(np.log2(self.fav_cnt)*10 * (self.character_level/100) +(self.character_level +5))
		self.SpD = int(np.log2(self.total_cnt)*10 * (self.character_level/100) +(self.character_level +5))
		sigmoid_time = 20-int(_.sigmoid(time_difference)*10)
		self.Spe = int(np.log2(sigmoid_time)*10 * (self.character_level/100) +(self.character_level +5))
		# self.enemy_name = 'ひよこ'
		return True
	def update_hp_gage(self):
		one_hp_gage = self.full_hp // 5
		if not self.rest_hp:
			self.hp_gage = '□□□□□'
		elif self.rest_hp < one_hp_gage:
			self.hp_gage = '■□□□□'
		elif self.rest_hp < 2* one_hp_gage:
			self.hp_gage = '■■□□□'
		elif self.rest_hp < 3* one_hp_gage:
			self.hp_gage = '■■■□□'
		elif self.rest_hp < 4* one_hp_gage:
			self.hp_gage = '■■■□□'
		elif self.rest_hp < 5* one_hp_gage:
			self.hp_gage = '■■■■□'
		else:
			self.hp_gage = '■■■■■'
		return True
	def calc_character_level(self):
		level_up_cnt = 0
		if self.exp is None:
			exp = 1
		if self.exp:
			exp_copy = self.exp
			exp_to_next_level = self.character_level ** 3
			while exp_copy > exp_to_next_level:
				exp_to_next_level = self.character_level ** 3
				exp_copy = exp_copy - exp_to_next_level
				self.character_level = self.character_level + 1
				level_up_cnt += 1 
			self.exp_to_level_up = exp_copy
		return level_up_cnt

class BattleGame():
	def __init__(self, name = '', enemy_name = None):
		self.name = name
		self.my_status = CharacterStatus(name)
		if enemy_name is None:
			self.enemy_name = self.my_status.enemy_name
		else:
			self.enemy_name = enemy_name
			self.my_status.enemy_name = enemy_name
		self.enemy_status = CharacterStatus(self.my_status.enemy_name)
	def main(self, text):
		ans_ls = []
		if self.my_status.mode == 'encount':
			ans_ls.append(self.encount(self.enemy_name))
		if self.my_status.mode == 'battle':
			ans_ls.append(self.battle(text))
			ans_ls.append(self.display())
		self.save_character_model(self.my_status.__dict__)
		self.save_character_model(self.enemy_status.__dict__)
		return '\n'.join(ans_ls)
	def save_character_model(self, status):
		try:
			core_sql.create_tables([CharacterStatusModel], True)
			with core_sql.transaction():
				try:
					character_status, created = CharacterStatusModel.get_or_create(name = status['name'])
					character_status = CharacterStatusModel(**status)
					character_status.save()
					core_sql.commit()
				except Exception as e:
					print(e)
		except IntegrityError as ex:
			print (ex)
			core_sql.rollback()
	def encount(self, enemy_name):
		enemy_character_level = self.my_status.character_level + 1
		self.enemy_status = CharacterStatus(enemy_name, character_level = enemy_character_level)
		self.my_status.enemy_name = enemy_name
		self.my_status.mode = 'battle'
		self.enemy_status.mode = 'battle'
		encount_type = '野生'
		ans = 'あっ、{}の{}があらわれた。'.format(encount_type, enemy_name)
		return ans
	def damage_hantei(self, Atker, damage):
		ans = ''
		rnd = np.random.randint(100)
		if damage < 0:
			damage = 0
			ans += Atker + 'の攻撃...' + 'こうかなし'
		elif rnd < 12:
			damage = damage * 2
			ans += Atker + 'の急所 -' + str(damage)
		elif rnd < 16:
			damage = 0
			ans += Atker + 'の攻撃...' + 'はずれ'
		else:
			ans += Atker + 'の攻撃 -' + str(damage)
		return ans, damage
	def battle(self, text = ''):
		def battle_enemy_turn(waza_value = 100, flag = '◉'):
			ans = ''
			try:
				randomed_damage = int(np.random.randint(15)) + 60
				base_damage = int(int((waza_value * int(self.enemy_status.character_level * 2 / 5) + 2 ) * self.enemy_status.Atk / self.my_status.Def)/ 50) + 2
				damage = int(base_damage * randomed_damage / 100)
			except Exception as e:
				print(e)
			ans, damage = self.damage_hantei(self.enemy_status.nickname, damage)
			ans = ''.join([flag, ans])
			self.my_status.rest_hp = self.my_status.rest_hp - damage
			if self.my_status.rest_hp < 0:
				self.my_status.rest_hp = 0
				self.my_status.status = 'Fainting'
			self.my_status.damage = damage
			self.my_status.update_hp_gage()
			return ans
		def battle_my_turn(waza_value = 100, flag = '◉'):
			ans = flag
			try:
				randomed_damage = int(np.random.randint(15)) + 60
				base_damage = int(int((waza_value * int(self.my_status.character_level * 2 / 5) + 2 ) * self.my_status.Atk / self.enemy_status.Def)/ 50) + 2
				damage = int(base_damage * randomed_damage / 100)
			except Exception as e:
				print(e)
			ans, damage = self.damage_hantei(self.my_status.nickname, damage)
			ans = ''.join([flag, ans])
			self.enemy_status.rest_hp = self.enemy_status.rest_hp - damage
			if self.enemy_status.rest_hp < 0:
				self.enemy_status.rest_hp = 0
				self.enemy_status.status = 'Fainting'
			self.enemy_status.damage = damage
			self.enemy_status.update_hp_gage()
			return ans
		random.seed(text)
		waza_value = random.randint(0, 150)
		ans_ls = []
		if self.my_status.Spe > self.enemy_status.Spe:
			ans_ls.append(battle_my_turn(flag = '🈜'))
			if not self.enemy_status.status == 'Fainting':
				ans_ls.append(battle_enemy_turn(waza_value, flag = '🈝'))
		else:
			ans_ls.append(battle_enemy_turn(flag = '🈜'))
			if not self.my_status.status == 'Fainting':
				ans_ls.append(battle_my_turn(waza_value, flag = '🈝'))
		self.my_status.enemy_name = self.enemy_status.name
		self.enemy_status.enemy_name = self.my_status.name
		self.my_status.mode = 'battle'
		self.enemy_status.mode = 'battle'
		return '\n'.join(ans_ls)
	def display(self):
		try:
			buf = ['ー', 
				''.join([self.enemy_status.nickname, 'Lv', str(self.enemy_status.character_level)]), 
				''.join([self.enemy_status.hp_gage, '[', str(self.enemy_status.damage), '↓']), 
				''.join(['HP', str(self.enemy_status.rest_hp), '/', str(self.enemy_status.full_hp)]), 
				''.join(['↑ー↓']), 
				''.join([self.my_status.nickname, 'Lv', str(self.my_status.character_level)]), 
				''.join([self.my_status.hp_gage, '[', str(self.my_status.damage), '↓']), 
				''.join(['HP', str(self.my_status.rest_hp), '/', str(self.my_status.full_hp)])
				]
			if self.enemy_status.rest_hp <= 0:
				kotaichi = 50
				addexp = int(kotaichi * self.enemy_status.character_level)
				buf.append(''.join([self.enemy_status.name , 'をたおした\n#END']))
				self.enemy_status.rest_hp = self.enemy_status.full_hp 
				self.my_status.enemy_name = 'あるぱか'
				self.my_status.mode = 'encount'
			elif self.my_status.rest_hp <= 0:
				buf.append(''.join([self.my_status.nickname, 'はたおれた\n#END']))
				self.my_status.enemy_name = self.enemy_status.name 
				self.my_status.mode = 'encount'
				self.my_status.rest_hp = self.my_status.full_hp
			else:
				buf.append('(任意のテキストで技発動)')
				self.my_status.enemy_name = self.enemy_status.name 
			ans = '\n'.join(buf)
			return ans
		except Exception as e:
			print('ERR.display', e)
			return ans
	
	def selectMode(self, text):
		if 'もどる' in text:
			p2 = 'back'
		elif 'へるぷ' in text:
			p2 = 'help'
		elif '2' in text:
			p2 = 'tool'
		elif 'かくにん' in text:
			p2 = 'status'
		elif '3' in text:
			p2 = 'status'
		elif 'にげる' in text:
			p2 = 'にげる'
		elif '4' in text:
			p2 = 'にげる'
		elif 'はじめから' in text:
			p2 = 'リセット'
		elif 'リセット' in text:
			p2 = 'リセット'
		elif '対戦' in text:
			p2 = 'encount'
		elif 'バトル' in text:
			p2 = 'encount'
		elif 'update' in text:
			p2 = 'update'
		elif 'リネーム' in text:
			p2 = 'rename'
		elif 'セーブ' in text:
			p2 = 'セーブ'
		elif 'へるぷ' in text:
			p2 = 'help'
		elif 'ツール' in text:
			p2 = 'tool'
		elif 'どうぐ' in text:
			p2 = 'tool'
		elif 'つーる' in text:
			p2 = 'tool'
		else:
			 p2 = 'battle'
		return p2
	
	def sendEXP(self, status):
		try:
			self.my_status.mode = 'battle' ## back
			print('データのセーブが完了。#END' + '#exp' + str(self.my_status.exp))
		except Exception as e:
			print(e)
			print('データのセーブに失敗。そんなこともありますよね。#END' + '#exp' + str(self.my_status.exp))
		return status
	
	def show_status(self, status):
		try:
			nextcharacter_levelExp = self.my_status.nextcharacter_levelExp
			exp = self.my_status.exp
			difexp = nextcharacter_levelExp - exp
			print(self.my_status.name)
			print('の能力値は...')
			print('self.character_level',self.my_status.selfharacter_level)
			# print('exp',self.my_status.exp)
			print('次Lvまで'+str(difexp)+'exp')
			print('hp', self.my_status.full_hp)
			print('Atk', self.my_status.Atk)
			print('Def', self.my_status.Def)
			print('SpA', self.my_status.SpA)
			print('SpD', self.my_status.SpD)
			print('Spe', self.my_status.Spe)
			print('\n1.わざ名 2.つーる\n3.もどる 4.にげる')
		except:
			print('測定不可。FF外か、データーベースが構築されていない')
	
	def selectModebyStatus(self, p2, status, enemy_status):
		mode = self.my_status.mode
		if mode == 'encount':
			p2 = 'encount'
		elif mode == 'battle':
			if self.my_status.Spe > self.enemy_status.Spe:
				p2 = 'battle.attack'
			else:
				p2 = 'battle.attacked'
		if p2 in {'battle.attacked', 'battle.attack'}:
			if mode == 'battle.attacked':
				p2 = 'battle.attacked'
			elif mode == 'battle.attack':
				p2 = 'battle.attack'
			else:
				p2 = p2
		return p2
	
	def old_main(self, text, me):
		enemy = 'あるぱか'
		p2 = self.selectMode(text)
		isSaveOK = True
		ans = ''
		try:
			# status, enemy_status = self.deal_status(me, enemy)
			status = self.my_status
			enemy_status = self.enemy_status
			# p2 = selectModebyStatus(p2, status, enemy_status)
		except Exception as e:
			print(e)
			# status = self.initialize_status(me)
			# enemy_status = self.initialize_status(enemy)
			status.mode = 'encount'
			self.save_character_model(status)
			self.save_character_model(enemy_status)
			return ans
		try:
			if p2 == 'encount' or self.my_status.mode == 'encount':
				cmds = text.split(' ')
				try:
					status, enemy_status = encount(me, enemy = cmds[1])
					ans += ''.join(['あ、やせいの',self.enemy_status.name,'があらわれた'])
				except Exception as e:
					print(e)
					status, enemy_status = encount(me, enemy)
					ans +=''.join(['あ、やせいの',self.enemy_status.name,'があらわれた'])
				self.my_status.hp_gage =  '■■■■■'
				status, enemy_status, ansD= display(status, enemy_status)
				self.my_status.mode = 'battle'
				ans += '\n'+ansD
			elif p2 == 'status':
				self.show_status(status)
			elif p2 == 'にげる':
				rnd = np.random.randint(100);
				if rnd < 80:
					ans += 'うまくにげられました。\nまたあそんでくださいね。#END'
					self.my_status.enemy = ''
					self.my_status.mode = 'encount'
				else:
					ans += 'にげられない'
					status, ans = display(status, enemy_status)
			elif p2 == 'リセット':
				ans += 'リセット完了#END'
			elif p2 == 'セーブ':
				status = sendEXP(status)
				self.my_status.mode = 'battle'
			elif p2 == 'rename':
				try:
					newname = text.split(' ')[1].replace('@', '')
					if len(newname)>5:
						ans += newname +' では文字数が長いです。5文字まででお願いします。'
					else:
						oldname = self.my_status.nickname
						self.my_status.nickname = newname
						ans += '「' + oldname+ '」から「'+ newname +'」にニックネームの変更が完了しました。\n'
					ans += '1.わざ名 2.つーる\n3.もどる 4.にげる'
				except Exception as e:
					print(e)
					ans +='その名前ではリネーム不可\n'
					ans +='1.わざ名 2.つーる\n3.もどる 4.にげる'
	
			elif p2 == 'recovery':
				rest_hp = self.my_status.rest_hp
				max_hp = self.my_status.full_hp
				status = recover(me)
				ans += '( •̀ ᴗ •́ )hpが全回復しました\n' + str(rest_hp) +'->' + str(max_hp)
				ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
	
			elif p2 == 'ほむまん':
				rest_hpB = self.my_status.rest_hp
				status = recover(me, 10)
				rest_hpA = self.my_status.rest_hp
				max_hp = self.my_status.full_hp
				ans += '( •̀ ᴗ •́ )hpが10回復しました。('+ str(rest_hpB) +'->' + str(rest_hpA) +')/'+ str(max_hp) +'	\代償として20経験値下げておきますね'
				status = getEXP(me, -20)
				ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
	
			elif p2 == '炭酸':
				status = recover(status, -10)
				ans += '( •̀ ᴗ •́ )怒 hpを10減らしました。炭酸はきらいです。'
				ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
			elif p2 == 'update':
				status = self.initialize_status(me)
				ans += 'ステータスをアップデートしました。\n'
				ans += '1.たたかう 2.つーる\n3.かくにん 4.にげる'
				self.my_status.mode = 'back'
			elif p2 == 'tool':
				ans += toolNote
	
			elif p2 == 'help':
				ans += helpNote
		
			elif p2 == 'back':
				ans += '行動を選択してください'
				status, ans = display(status, enemy_status)
				self.my_status.mode = 'back'
		
			else:
				random.seed(text)
				waza_value = random.randint(0, 150)
				if self.my_status.Spe > self.enemy_status.Spe:
					enemy_status, status, ansB1 = battle(enemy_status, status, flag = '🈜')
					status, enemy_status, ansB2 = battle(status, enemy_status, waza_value, flag = '🈝')
					status, enemy_status, ansD = display(status, enemy_status)
					ans += ansB1 +'\n' + ansB2 +'\n'+ ansD
				else:
					status, enemy_status, ansB1 = battle(status, enemy_status, flag = '🈜')
					enemy_status, status, ansB2 = battle(enemy_status, status, waza_value, flag = '🈝')
					status, enemy_status, ansD = display(status, enemy_status)
					ans += ansB1 +'\n' + ansB2 +'\n'+ ansD
		except Exception as e:
			print(e)
			try:
				try:
					ans += '( •̀ ᴗ •́ )あ、敵は逃げてしまいました。また今度にしましょう。とりあえず、オートセーブしておきました。再開する場合は「うみもん」で。バグったら「リセット」#END' + '#exp' + str(self.my_status.exp)
				except Exception as e:
					print(e)
					ans += '( •̀ ᴗ •́ )あ、敵は困って逃げてしまいました。また今度にしましょう。 再開する場合は「うみもん」で。バグったら「リセット」#END'
				status = self.initialize_status(me)
				enemy_status = self.initialize_status(enemy)
			except Exception as e:
				print(e)
				ans +='( •̀ ᴗ •́ )バグ発生。\n そんなこともありますよね。そのうち直しておきますね #END'
	
		if isSaveOK:
			self.save_character_model(status)
			self.save_character_model(enemy_status)
		return ans
if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		text = argvs[1]
		user = argvs[2]
	except:
		user = 'p_eval'
		text = "皇居"
	# p(CharacterStatus('アルパカあああ').__dict__)
	battle_game = BattleGame('h_y_ok', 'chana1031')
	ans = battle_game.main(text)
	print(ans)
	# cmdlist = text.split(' ')
	# text = cmdlist[0]
	# ret = SRTR(text, user)
	# print(ret)

	# word = 'askww'
	# ejje_url = ''.join(["http://ejje.weblio.jp/content/", word])
	# html = urllib.request.urlopen(ejje_url)
	
	# soup = bs4.BeautifulSoup(html, "lxml")
	# print(soup.find('div', class_ = "summaryM"))
	# print(str(soup.find("div", class_ = "summaryM")).split('</b>')[1][:-6])
		# print('abcde'[:-1])
	# core_sql.close()