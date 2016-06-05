#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import subprocess
# import scipy as sp
import datetime # datetimeモジュールのインポート
# from pymongo import MongoClient
import numpy as np
import sqlite3
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
database = SqliteExtDatabase('../umiA.sqlite3', autocommit=False, journal_mode='persist')
database.connect()

class BaseModel(Model):
    class Meta:
        database = database

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

class monStatus(BaseModel):
	name = CharField(primary_key=True)
	nickname= CharField(null=True)
	exp = IntegerField(null=True)
	LV = IntegerField(null=True)
	nextLVExp = IntegerField(null=True)
	damage = IntegerField(null=True)
	HP = IntegerField(null=True)
	restHP = IntegerField(null=True)
	HPgage= CharField(null=True)
	Atk = IntegerField(null=True)
	Def = IntegerField(null=True)
	SpA = IntegerField(null=True)
	SpD = IntegerField(null=True)
	Spe = IntegerField(null=True)
	enemy_name = CharField(null=True)
	class Meta:
		 db_table = 'mon_status'
# # MongoDBへの接続
# mongo_client = MongoClient('localhost:27017')
# # データベースの選択
# db = mongo_client["Umi_IA"]
# userinfosDB = db["userinfos"]
# twlog_sql = db["tweets"]
# twmonsDB = db["twmons"]

toolNote = '''=ツール=
1.たたかう 2.ツール
3.かくにん 4.にげる
5.セーブ 6.リセット
7.あぷで 7.おわり
=設定=
1.リネーム XX
2.エンカウント @ XX
3.へるぷ
=道具=
1.ほむまん 2. 炭酸
3.リカバリ '''

helpNote = '''( •̀ ᴗ •́ )うみもん(海未っ)
<未編集場所...>
おとのきざかもんすたーず、略して「うみもん(仮)」
取説を読んでくださいね。
バグは多いです。レベル調整もまだです。
ごめんなさい、諦めてください。
コマンドを入力してください。
1.たたかう 2.つーる
3.かくにん 4.にげる'''

def sigmoid(z):
  return 1/(1+np.exp(-z)) if -100. < z else 0.

def HPgager(restHP, fullHP):
	aHPgage = fullHP//5
	if restHP == 0:
		HPgage = '□□□□□'
	elif restHP < aHPgage:
		HPgage = '■□□□□'
	elif restHP < 2* aHPgage:
		HPgage = '■■□□□'
	elif restHP < 3* aHPgage:
		HPgage = '■■■□□'
	elif restHP < 4* aHPgage:
		HPgage = '■■■□□'
	elif restHP < 5* aHPgage:
		HPgage = '■■■■□'
	else:
		HPgage = '■■■■■'
	return HPgage

def readStatus(user = 'masaMikam'):
		try:
			# tempUDB = contextDB.find({'name': user})[0]
			database.create_tables([monStatus], True)
			with database.transaction():
				try:
					status, created = monStatus.get_or_create(name = user)
					# print(status)
					return status
				except Exception as e:
					print(e)
				database.commit()
		# srtrdb = tempUDB['srtr']
		except Exception as e:
			database.rollback()

def readUDB(user = 'masaMikam'):
		try:
			# tempUDB = contextDB.find({'name': user})[0]
			# database.create_tables([Users], True)
			with database.transaction():
				try:
					status= Users.select().where(Users.screen_name == user).get()
					# print(status.time)
					return status
				except Exception as e:
					print(e)
				database.commit()
		# srtrdb = tempUDB['srtr']
		except Exception as e:
			database.rollback()


def init(name, LV = 0, isSave = False):
	# userinfoデータよみだし
	status = {}
	try:
		userinfo = readUDB('masaMikam')
		lasttime = userinfo.time
		# twtrinfo = userinfo['twitter']
		totalcnt = userinfo.totalcnt+1
		friends_cnt = userinfo.friends_cnt+1
		followers_cnt = userinfo.followers_cnt+1
		statuses_cnt = userinfo.statuses_cnt+1
		fav_cnt = userinfo.fav_cnt+1
		status['name'] = name
		status['nickname'] = userinfo.name[:5]
	except Exception as e:
		# print(e)
		totalcnt = 1
		lasttime = 1
		friends_cnt = 100
		followers_cnt = 100
		statuses_cnt = 100
		fav_cnt = 100
		status['name'] = name
		status['nickname'] = name
	try:
		exp = userinfo.exp
		if exp == 0:
			exp = totalcnt *100
	except:
		exp = totalcnt *100
	# 計算式
	d = datetime.datetime.today()
	nowtime = d.strftime("%Y%m%d%H%M%S")
	difT = (int(nowtime)-int(lasttime) - 100) // 60
	Spe = 20-int(sigmoid(difT)*10)
	# print(exp)
	status['exp'] = exp
	if LV == 0:
		status =  calcLv(status)
		LV = status['LV']
	else:
		status['LV'] = LV
		status['nextLVExp'] = 0
	status['damage'] = 0
	status['mode'] = 'encount'
	fullHP = int(np.log2(statuses_cnt)*10 * (LV/100) +(LV +10))
	restHP = fullHP
	status['HP'] = fullHP
	status['restHP'] =restHP
	status['HPgage'] = HPgager(restHP, fullHP)
	status['Atk'] = int(np.log2(friends_cnt)*10 * (LV/100) +(LV +5))
	status['Def'] = int(np.log2(followers_cnt)*10 * (LV/100) +(LV +5))
	status['SpA'] = int(np.log2(fav_cnt)*10 * (LV/100) +(LV +5))
	status['SpD'] = int(np.log2(totalcnt)*10 * (LV/100) +(LV +5))
	status['Spe'] = int(np.log2(Spe)*10 * (LV/100) +(LV +5))
	status['enemy_name'] = 'AlpkS'
	print(status)
	return status

def calcLv(status):
	exp = status.exp
	if exp == None:
		exp = 1
	if exp != 0:
		nLv = 10
		LV = 0
		while exp > nLv:
			nLv = LV ** 3
			exp = exp - nLv
			LV = LV + 1
	else:
		LV = 10
	LvList = [(lv) ** 3 for lv in range(LV+1)]
	nextLVExp = sum(LvList)
	# status = status
	status.nextLVExp = nextLVExp
	status.LV = LV
	return status

def getStatus(name):
	try:
		status = readStatus(name)
	except:
		status = init(name)
	# status = dealStatus(status)
	return status

def dealStatus(name, enemy):
	status = getStatus(name)
	try:
		LV = status.LV
		if LV == None:
			LV = 0
		status = calcLv(status)
		altLV = status.LV
		enemy_name = status.enemy_name
		if altLV > LV:
			upLV = altLV - LV
			print('LVが'+str(upLV)+'上がりました！！！次エンカウント時にステータスが上昇します。')
	except:
		enemy_name = None
	enemyLV = status.LV - 1
	if enemy_name == None:
		enemy_name = enemy
		e_status = init(enemy, enemyLV)
	else:
		e_status = readStatus(enemy_name)

	print(status.HP)
	# status['enemy'] = e_status
	return status, e_status


def encount(me, enemy):
	try:
		mystatus = twmonsDB.find({'_id':me})[0]
	except Exception as e:
		print(e)
		mystatus = init(me)
		print('データがないです。新しく作り直しますね。')
	enemyLV = mystatus['LV'] - 1
	e_status = init(enemy, enemyLV)
	mystatus['enemy'] = e_status
	return mystatus, e_status

def recover(name, amount = 1000):
	status, statusE = getStatus(name)
	maxHP = status['HP']
	restHP = status['restHP']

	if restHP + amount > maxHP:
		amount = maxHP - restHP
	twmonsDB.update_one({'_id': name},{'$inc': {'restHP': amount}}, upsert =True)
	status, statusE = getStatus(name)
	return status

def getEXP(name, amount):
	twmonsDB.update_one({'_id': name},{'$inc': {'exp': amount}}, upsert =True)
	if amount > 0:
		print(str(amount) + 'exp獲得')
	else:
		print(str(-amount) + 'exp減少')
	status, statusE = getStatus(name)
	return status

def battle(status, statusE, waza = 100):
	waza = 100
	rnd = np.random.randint(100);
	rndDMG = int(np.random.randint(15)) + 60;
	restHP = status['restHP']
	Atk = status['Atk']
	damage = Atk- status['Def']
	Atker = statusE['nickname']
	kisoDMG = int(int((waza * int(statusE['LV'] * 2 / 5) + 2 ) * Atk / status['Def'])/ 50) + 2

	damage = int(kisoDMG * rndDMG / 100)
	if damage < 0:
		damage = 0
		print(Atker + 'の攻撃...' + 'こうかなしです')
	elif rnd < 16:
		damage = 0
		print(Atker + 'の攻撃...' + 'はずれました')
	elif rnd < 12:
		damage = damage*2
		print(Atker + 'の攻撃 ' + 'きゅうしょ' + str(damage) + 'ダメ')
	else:
		print(Atker + 'の攻撃 ' + str(damage) + 'ダメ')

	restHP = restHP - damage
	if restHP < 0:
		restHP = 0
	fullHP = status['HP']
	status['restHP'] = restHP
	status['damage'] = damage
	status['HPgage'] = HPgager(restHP, fullHP)
	return status

def display(status, statusE):
	# print(statusE)
	restHPe = statusE.restHP
	me = status.name
	mynickname = status.nickname
	print('ー')
	print(statusE.nickname, 'Lv'+str(statusE.LV))
	print(statusE.HPgage, '['+str(statusE.damage)+'↓')
	print('HP', str(restHPe)+'/'+str(statusE.HP))
	print('↑ー↓')
	print(status.nickname, 'Lv'+str(status.LV))
	print(status.HPgage,'['+str(status.damage)+'↓')
	restHP = status.restHP
	print('HP', str(restHP)+'/'+str(status.HP))
	if restHPe == 0:
		kotaichi = 50
		addexp = int(kotaichi * statusE.LV)
		print(statusE.name + 'をたおした( •̀ ᴗ •́ )')
		status = getEXP(me, addexp)
		status.enemy_name = ''
		status.mode = 'encount'
	elif restHP != 0:
		print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		status.enemy_name = ''
	else:
		print(mynickname,'はたおれた\nめのまえがまっくらになった\n( •̀ ᴗ •́ ) #END')
		status.enemy_name = ''
		status.mode = 'encount'
		maxHP = status.HP
		status.restHP = maxHP
	return status

def selectMode(text):
	if 'たたかう' in text:
		p2 = ''
	elif '1' in text:
		p2 = ''
	elif 'へるぷ' in text:
		p2 = 'help'
	elif '2' in text:
		p2 = 'help'
	elif 'かくにん' in text:
		p2 = 'status'
	elif '3' in text:
		p2 = 'status'
	elif 'にげる' in text:
		p2 = 'にげる'
	elif '4' in text:
		p2 = 'にげる'
	elif 'リカバリ' in text:
		p2 = 'recovery'
	elif 'ほむまん' in text:
		p2 = 'ほむまん'
	elif '炭酸' in text:
		p2 = '炭酸'
	elif 'はじめから' in text:
		p2 = 'リセット'
	elif 'リセット' in text:
		p2 = 'リセット'
	elif 'エンカウント' in text:
		p2 = 'encount'
	elif 'リネーム' in text:
		p2 = 'rename'
	elif 'セーブ' in text:
		p2 = 'セーブ'
	elif 'アプデ' in text:
		p2 = 'update'
	elif 'あぷで' in text:
		p2 = 'update'
	elif 'update' in text:
		p2 = 'update'
	elif 'へるぷ' in text:
		p2 = 'help'
	elif 'ツール' in text:
		p2 = 'tool'
	elif 'どうぐ' in text:
		p2 = 'tool'
	elif 'つーる' in text:
		p2 = 'tool'
	else:
		 p2 = 'back'
	return p2

def reset(name):
	isSaveOK = False
	try:
		twmonsDB.remove({'_id': name})
		print('( •̀ ᴗ •́ )データをリセットしました。「たたかう」で新しいデータから開始します。')
	except Exception as e:
		# print(e)
		print('( •̀ ᴗ •́ )データをリセットに失敗しました。')
	return isSaveOK

def sendEXP(status):
	try:
		status['mode'] = 'battle' ## back
		print('( •̀ ᴗ •́ )データのセーブが完了しました。#END' + '#exp' + str(status['exp']))
	except Exception as e:
		# print(e)
		print('( •̀ ᴗ •́ )データのセーブに失敗しました。そんなこともありますよね。#END' + '#exp' + str(status['exp']))
	return status

def showStatus(status):
	try:
		nextLVExp = status['nextLVExp']
		exp = status['exp']
		difexp = nextLVExp-exp
		print('( •̀ ᴗ •́ )',status['name'])
		print('の能力値は...')
		print('LV',status['LV'])
		# print('exp',status['exp'])
		print('次Lvまで'+str(difexp)+'exp')
		print('HP', status['HP'])
		print('Atk', status['Atk'])
		print('Def', status['Def'])
		print('SpA', status['SpA'])
		print('SpD', status['SpD'])
		print('Spe', status['Spe'])
		print('ーーです。\n1.たたかう 2.つーる\n3.かくにん 4.にげる')
	except:
		print('測定できません。フォローされていないか、データーベースが構築されていないかだと思います...')

def selectModebyStatus(p2, status):
	if p2 !='':
		p2 = p2 
	else:
		mode = status.mode
		if mode == 'encount':
			p2 = 'encount'
		elif mode == 'battle':
			# if status['Spe'] > status['enemy']['Spe']:
			# 	p2 = 'battle.attack'
			# else:
			p2 = 'battle.attacked'
		elif mode == 'battle.attack':
			p2 = 'battle.attack'
		elif mode == 'battle.attacked':
			p2 = 'battle.attacked'
		else:
			p2 = 'back'
	return p2

def Main(text, me, enemy = 'アルパカ'):
	p2 = selectMode(text)
	isSaveOK = True
	try:
		# status = getStatus(me)
		status, statusE = dealStatus(me, enemy)
		p2 = selectModebyStatus(p2, status)
	except Exception as e:
		print('( •̀ ᴗ •́ )おとのきざかモンスター`s[海未](通称:うみもん)のせかいへようこそ。[β版]\n 進行役の園田海未です。私となかよくしたり、ふぁぼったり、ツイートしたり、ゲームであそんだりすると強くなれますよ。\n「たたかう」と返信して、さぁ修行ですっ！！')
		status = init(me)
		e_status = init(enemy)
		status['enemy'] = e_status
		status['mode'] = 'encount'
		save(status, me)
		return
	# print(status)
	print(p2)
	try:
		if p2 == 'status':
			showStatus(status)
		elif p2 == 'リセット':
			isSaveOK = reset(me)
		elif p2 == 'セーブ':
			status = sendEXP(status)
			status['enemy'] = statusE
			status['mode'] = 'battle'
			# print(status)
		elif p2 == 'rename':
			try:
				newname = cmdlist[1].replace('@', '')
				if len(newname)>5:
					print('文字数が長いです。5文字まででお願いします。')
				else:
					oldname = status['nickname']
					status['nickname'] = newname
					print('( •̀ ᴗ •́ )'+oldname+ 'から'+ newname +'にニックネームの変更が完了しました。')
				print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
			except:
				print('( •̀ ᴗ •́ )その名前ではリネームできません')
				print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'encount':
			try:
				enemy = cmdlist[1].replace('@', '')
				status, statusE = encount(me, enemy)
				print('( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました')
			except Exception as e:
				status, statusE = encount(me, enemy)
				print('( •̀ ᴗ •́ )あ、やせいの\n',statusE['name'],'\nがあらわれました')
			status['HPgage'] =  '■■■■■'
			status = display(status, statusE)
			status['enemy'] = statusE
			status['mode'] = 'battle'

		elif p2 == 'recovery':
			restHP = status['restHP']
			maxHP = status['HP']
			status = recover(me)
			print('( •̀ ᴗ •́ )HPが全回復しました\n' + str(restHP) +'->' + str(maxHP))
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')

		elif p2 == 'ほむまん':
			restHPB = status['restHP']
			status = recover(me, 10)
			restHPA = status['restHP']
			maxHP = status['HP']
			print('( •̀ ᴗ •́ )HPが10回復しました。('+ str(restHPB) +'->' + str(restHPA) +')/'+ str(maxHP) +'\代償として20経験値下げておきますね')
			status = getEXP(me, -20)
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')

		elif p2 == '炭酸':
			status = recover(status, -10)
			print('( •̀ ᴗ •́ )怒 HPを10減らしました。炭酸はきらいです。')
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'update':
			status = init(me)
			print('( •̀ ᴗ •́ )ステータスをアップデートしました。')
			print('1.たたかう 2.つーる\n3.かくにん 4.にげる')
		elif p2 == 'battle.attacked':
			status = battle(status, statusE)
			statusE = battle(statusE, status)
			status['mode'] = 'battle.attack'
			status = display(status, statusE)
			status['enemy'] = statusE
		elif p2 == 'battle.attack':
			statusE = battle(statusE, status)
			status = battle(status, statusE)
			status['mode'] = 'battle.attacked'
			status = display(status, statusE)
			status['enemy'] = statusE

		elif p2 == 'tool':
			print(toolNote)

		elif p2 == 'help':
			print(helpNote)
	
		elif p2 == 'back':
			print('( •̀ ᴗ •́ )行動を選択してください')
			status = display(status, statusE)
			status['mode'] = 'back'
			status['enemy'] = statusE
	
		elif p2 == 'にげる':
			rnd = np.random.randint(100);
			if rnd < 80:
				print('うまくにげられました。\n( •̀ ᴗ •́ )またあそんでくださいね。#END')
				status['enemy'] = ''
				status['mode'] = 'encount'
			else:
				print('( •̀ ᴗ •́ ) にげられないです')
				status = display(status, statusE)
		else:
			status, statusE = battle(me, enemy)
			status = display(status, statusE)
	except Exception as e:
		print(e)
		try:
			try:
				print('( •̀ ᴗ •́ )あ、敵は逃げてしまいました。また今度にしましょう。とりあえず、オートセーブしておきました。再開する場合は「うみもん」で。バグったら「リセット」#END' + '#exp' + str(status['exp']))
			except:
				print('( •̀ ᴗ •́ )あ、敵は困って逃げてしまいました。また今度にしましょう。 再開する場合は「うみもん」で。バグったら「リセット」#END')
			isSaveOK = reset(me)
		except Exception as e:
			# print(e)
			print('( •̀ ᴗ •́ )バグ発生です。\n そんなこともありますよね。そのうち直しておきますね #END')
	# DB
	# try:
	# 	status['enemy'] = statusE
	# except Exception as e:
	# 	status['enemy'] = ''
	
	if isSaveOK == True:
		save(status, me)

def save(status, name):
	try:
		del status['_id']
		twmonsDB.update_one({'_id': me},{'$set': status}, upsert =True)
	except Exception as e:
		twmonsDB.update_one({'_id': me},{'$set': status}, upsert =True)

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		me = argvs[1]
		intext = argvs[2]
	except:
		me = 'masaMikam'
		intext = 'リセット'
		intext = 'エンカウント KOTORI'
		intext = 'セーブ'
		intext = 'たたかう'
	cmdlist = intext.split(' ')
	text = cmdlist[0]
	enemy = 'アルパカ'
	# init('masaMikam')
	# メイン
	Main(text, me, enemy)
	# getEXP('masaMikam', 1000000)

