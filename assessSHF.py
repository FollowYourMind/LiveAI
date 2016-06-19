#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import subprocess
# PROJECT_PATH='/Users/masa/Dropbox/Project/Python/Umi_bot'
# sys.path.append(PROJECT_PATH+'/modules')
# sys.path.append(PROJECT_PATH+'/Data')
import datetime # datetimeモジュールのインポート
import random
from pymongo import MongoClient
import numpy as np
import scipy as sp

import natural_language_processing
import re

# MongoDBへの接続
mongo_client = MongoClient('localhost:27017')
# データベースの選択
db = mongo_client["Umi_IA"]
wordsDB = db["words"]
tempDB = db["temp"]

def two_list_to_dict(key_list, val_list):
  return dict(zip(key_list, val_list))

def SHFdict(SHdict, stakeholders, valuelist, kind):
	i = 0
	for stakeholder in stakeholders:
		value = valuelist[i]
		if kind != '':
			value = str2float(value)
		# print(value)
		SHdict[stakeholder][kind] = value
		i = i + 1
	return SHdict
# tempDB.remove({'name': user})

def Main(s, user):
	temp = {}
	temp['plan'] = {}
	try:
		tempdb = tempDB.find_one({'name': user})
		SHdict = tempdb['plan']['SH']
		var = tempdb['plan']['phase']
		stakeholders = tempdb['plan']['SHlist']
		valuelist = s.split("\n")
		nextPhase = var
		if s == '':
			print('( •̀ ᴗ •́ )なにか言ってくれないとわからないです。')
		elif s == 'おわり':
 			tempDB.remove({'name': user})
		 	print('( •̀ ᴗ •́ )FATを終わりにします。#END')
		 	stakeholders  = ''
		 	nextPhase  = ''
		elif var == 'start':
			try:
				i = 0
				for a in valuelist:
					SHdict[a] = {}
					i = i + 1
				temp['plan']['SH'] = SHdict
				stakeholders = valuelist
				print('利害関係者は'+ str(valuelist) +'ですね？')
				print('ーーー')
				print('1/5]( •̀ ᴗ •́ )次に、各主体の「立場」を改行で教えてください。\n賛成 or 反対 or 中立\n[例]->\n賛成\n反対\n賛成\n反対')
				print('ーーー')
				print('< もどる >< おわり >')
				nextPhase = 'k'
			except Exception as e:
				print('1/5err]ダメです。もう一度！')
				nextPhase = 'start'
		elif var == 'k':
			try:
				if 'もどる' in s:
					print('( •̀ ᴗ •́ )ステークホルダー再設定に戻ります。\n各利害関係者を改行で列記してください。\n[例]CDを買うという計画\n例]\n穂乃果\n凛\n希\n鳥')
					nextPhase = 'start'
					stakeholders  = ''
				else:
					print('者:立場|')
					kstr = '不明'
					i = 0
					for a in stakeholders:
						adata = SHdict[a]
						value = valuelist[i]
						if '賛' in value:
							adata['k'] = 1
							kstr = '賛成'
						elif '反' in value:
							adata['k'] = -1
							kstr = '反対'
						else:
							adata['k'] = 0
							kstr = '中立'
						i = i + 1
						adata['kstr'] = kstr
						print(a + ': ' + kstr + ' | [　]')
					print('ーーー')
					print('2/5] 次は、各主体の賛成・反対の意見表明「確率」を教えてください。0〜10です。小数もOKです。[例]-> \n2\n3\n4.7\n1')
					print('< もどる >< おわり >')
					nextPhase = 'w'
			except Exception as e:
				# print(e)
				print('2/5err]ダメです。もう一度！')
				nextPhase = 'k'
		elif var == 'w':
			try:
				if 'もどる' in s:
					print('「立場」再設定に戻ります。\n各主体の「立場」を改行で教えてください。\n賛成 or 反対 or 中立\n[例]->\n賛成\n反対\n賛成\n反対')
					nextPhase = 'k'
				else:
					i = 0
					print('者:立場|確率|')
					for a in stakeholders:
						value = valuelist[i]
						value = str2float(value)
						adata = SHdict[a]
						adata['w'] = value/10
						print(a + ': ' + adata['kstr']+ ' | ' + str(adata['w']) + ' | [　]')
						i = i + 1	
					print('ーーー')
					print('3/5] 次は、各主体の行動の「可能性」を改行で教えてください。0〜10です。小数もOKです。[例]-> \n2\n3\n4.7\n1')
					print('< もどる >< おわり >')
					nextPhase = 'p'
			except Exception as e:
				# print(e)
				print('3/5err]ダメです。もう一度！')
				nextPhase = 'w'
		elif var == 'p':
			try:
				if 'もどる' in s:
					print('賛成・反対の意見表明「確率」再設定に戻ります。\n各主体の賛成・反対の意見表明「確率」を教えてください。0〜10です。小数もOKです。[例]-> \n2\n3\n4.7\n1')
					nextPhase = 'w'
				else:
					i = 0
					print('者:立場|確率|可能性')
					for a in stakeholders:
						value = valuelist[i]
						value = str2float(value)
						adata = SHdict[a]
						adata['p'] = value/10
						print(a + ': ' + adata['kstr'] + ' | ' + str(adata['w']) + ' | ' + str(adata['p']) + ' | [　]')
						i = i + 1	
					print('ーーー')
					print('4/5]( •̀ ᴗ •́ )一番「つよい」主体を10としたときの他主体の相対的な「つよさ」を教えてください。改行でお願いします。0〜10です。小数もOKです。[例]-> \n2\n3\n4.7\n10')
					print('< もどる >< おわり >')
					nextPhase = 's'
			except Exception as e:
				# print(e)
				print('4/5err]ダメです。もう一度！')
				nextPhase = 'p'
		elif var == 's':
			try:
				if 'もどる' in s:
					print('行動の「可能性」再設定に戻ります。\n各主体の行動の「可能性」を改行で教えてください。0〜10です。小数もOKです。[	例]-> \n2\n3\n4.7\n1')
				else:
					i = 0
					print('者:立場|確率|可能性|強さ')
					for a in stakeholders:
						value = valuelist[i]
						value = str2float(value)
						adata = SHdict[a]
						adata['s'] = value /10
						print(a + ': ' + adata['kstr'] + ' | ' + str(adata['w']) + ' | ' + str(adata['p']) + ' | ' + str(adata['s']))
						i = i + 1
						adata['F'] = adata['k'] * adata['w'] * adata['p'] * adata['s']
					print('ーーー')
					print('5/5]( •̀ ᴗ •́ )終了ですっ。計算しています。結果は...')
					print('< もどる >< おわり >< つぎへ >')
					nextPhase = 'TF'
			except Exception as e:
				print('5/5err]ダメです。もう一度！')
				nextPhase = 's'
		elif var == 'TF':
			try:
				if 'もどる' in s:
					print('( •̀ ᴗ •́ )各主体の「相対的資源順位」再設定に戻ります。\n一番「つよい」主体を10としたときの他主体の相対的な「つよさ」を教えてください。改行でお願いします。0〜10です。小数もOKです。[	例]-> \n2\n3\n4.7\n1')
					nextPhase = 's'
				else:
					print('[Feasibility]')
					TF = 0
					for a in stakeholders:
						adata = SHdict[a]
						print(a + ': ' + str(adata['F']))
						TF += adata['F']
					TF = TF/len(stakeholders)
					if TF > 0:
						print('結論] ( •̀ ᴗ •́ )実施可能です。\nTF: '+ str(TF) + ' > 0\nおわります。#END')
					else:
						print('結論] ( •̀ ᴗ •́ )実施不可能です。\nTF: '+ str(TF) + ' < 0\nおわります。#END')
					nextPhase = ''
					tempDB.remove({'name': user})
			except Exception as e:
				print('err 初期化します。')
		else:
			print('( •̀ ᴗ •́ )実現可能性評価法(FAT)チュートリアルをはじめます。\n利害関係者の衝突から計画の実現可能性を見積もります。\nまず、各利害関係者を改行で列記してください。\n例]\n穂乃果\n凛\n希\n鳥')
			nextPhase = 'start'
			stakeholders = ''

	except Exception as e:
		# print(e)
		SHdict = {}
		temp['plan']['SH'] = SHdict
		stakeholders = ''
		nextPhase = ''

	temp['plan']['phase'] = nextPhase
	temp['plan']['SHlist'] = stakeholders
	temp['plan']['SH'] = SHdict
	tempDB.update_one({'name': user},{'$set': temp}, upsert =True)

def str2float(s, init = 1):
	try:
		num = re.match("\d*\.\d*",s)
		if num == None:
			num = re.match("\d*",s)
		extracted = num.group()
		extnum = float(extracted)
		return extnum
	except:
		return init

def getSHs(s, SHdict = {}):
	stakeholders = s.split(' ')
	for stakeholder in stakeholders:
		SHdict[stakeholder] = {}
	return SHdict

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		intext = argvs[1]
		user = argvs[2]
	except:
		user = 'p_eval'
		intext = 'A\nB\nC'
		# intext = 'もどる'
		# intext = 'おわり'
		# intext = '賛成\n反対\n賛成'
	# user = 'masaMikam'
	# print(intext, user)
	Main(intext, user)
	print('#FAT')