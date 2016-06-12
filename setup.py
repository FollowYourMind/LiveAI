#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import io
import subprocess
import multiprocessing
import threading
import importlib
import json
import re
import shutil
import time
import urllib
import bs4
import pprint
from datetime import datetime, timedelta
from collections import Counter, deque
from itertools import chain
#logging
from logging import getLogger,StreamHandler,DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
#math
import numpy as np
import requests
# 各種ライブラリをインポート
import tweepy

import _

THISPATH = _.get_thispath()
PROJECTPATH = _.get_projectpath()

#configurationを読み込み or 生成
config_place = THISPATH + '/config.json'
cfg = {}
cfg = _.get_json(place = config_place, backup_place = None)
managerID = cfg['managerID']
DATADIR = cfg['DATADIR']
tmp = {}
#tempFileを読み込み or 生成
TEMPJSONPLACE = DATADIR + "/tmp.json"
bkupTEMPJSONPLACE = DATADIR + "/tmp_bkup.json"
bkup2TEMPJSONPLACE = DATADIR + "/tmp_bkup2.json"
TMP_CONFIG_PLACE = DATADIR + "/tmp_config.json"
TMP_STATS_PLACE = DATADIR + "/tmp_stats.json"
# def load_json(place):
# 	try:
# 		with open(place, "r", encoding='utf-8') as tmpjson:
# 			return json.load(tmpjson)
# 	except Exception as e:
# 		print(e)
# 		with open(place, "w", encoding='utf-8') as tmpjson:
# 			json.dump({},tmpjson, ensure_ascii=False, sort_keys=True, indent = 4, default = _.support_datetime_default)
# 			return {}
# tmp = load_json(TEMPJSONPLACE)
# tmp_config = TMP_CONFIG_PLACE

DIRIMGfeedback = DATADIR + '/imgs/feedback/'
DIRIMGtmp = DATADIR + '/imgs/feedback/tmp'
DIRIMGundefined = DATADIR + '/imgs/feedback/undefined'
DIRusers = DATADIR + '/user'

#DBs
# twlog_sql_PLACE = DATADIR + '/SQL/sys.twlog'
# core_sql_PLACE = DATADIR + '/SQL/sys.info'
# talk_sql_PLACE = DATADIR + '/SQL/sys.talk'
# wordnet_sql_PLACE =DATADIR + '/lib/wnjpn.db'
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
# modelmachine_learning_img = DATADIR + '/ML_Brain/DNN_1-3_8'
modelSVM = DATADIR + '/lib/SVM_us/SVMmodel2.pkl'
testpic = DATADIR + '/imgs/maki/sr-maki-cool-shoki-go.jpg'

cascade_lib_anime = DATADIR + '/lib/lbpcascade_animeface.xml'
cascade_lib_cat = DATADIR + '/lib/cascade_lib_cat.xml'

character = '海未'
chara_list = ['凛', '雪穂', '海未', '真姫', '穂乃果', '絵里', '花陽']
chara_set = set(chara_list)
NICKNAMES = {
	'おてつだい穂乃果':'穂乃果',
	'おて穂乃':'穂乃果',
	'お手穂乃':'穂乃果',
	'おてほの':'穂乃果',
	'おてつだい海未':'海未',
	'おて海未':'海未',
	'お手海未':'海未',
	'おてうみ':'海未',
	'おてつだい凛':'凛',
	'おて凛':'凛',
	'お手凛':'凛',
	'おてりん':'凛',
	'おてつだい真姫':'真姫',
	'おて真姫':'真姫',
	'お手真姫':'真姫',
	'おてまき':'真姫',
	'おてつだい雪穂':'雪穂',
	'おて雪穂':'雪穂',
	'お手雪穂':'雪穂',
	'おてゆきほ':'雪穂',
	'おてつだい絵里':'絵里',
	'おて絵里':'絵里',
	'お手絵里':'絵里',
	'おてえり':'絵里',
	'おてつだいちゃな':'ちゃな',
	'おてぱな': '花陽',
	'おてはなよ': '花陽',
	'おて花陽': '花陽',
	'お手ぱな': '花陽',
	'おてのぞ': '希',
	'おて希': '希',
	'おてつだい希': '希',
	'おてこと': 'ことり',
	'おてちゅん': 'ことり',
	'おてつだいことり': 'ことり',
	'おてにこ': 'にこ',
	'おて矢澤': 'にこ',
	'おてつだいにこ': 'にこ',
}
def iscalledBOT(text, select_set = {''}):
	bot_called_ls = [(bot_key in text and bot_value in select_set, bot_value) for bot_key, bot_value in NICKNAMES.items()]
	return [pairs[1] for pairs in bot_called_ls if pairs[0]]
