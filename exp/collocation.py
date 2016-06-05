#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from collections import Counter
import natural_language_processing
import re
import random
import numpy as np
from itertools import chain
# from numba import double
# from numba.decorators import jit

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
db = SqliteExtDatabase('../twtrData.sqlite3', autocommit=False, journal_mode='persist')
db.connect()
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

class BaseModel(Model):
    class Meta:
        database = db
class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)
    class Meta:
        database = db

def clean_text(text):
	text = re.sub(r'(@[^\s　]+)', '', text)
	text = re.sub(r'(#[^\s　]+)', '', text)
	text = re.sub(r'(http[^\s　]+)', '', text)
	text = re.sub(r'(^[\s　]+)', '', text)
	text = re.sub(r'([\s　]+$)', '', text)
	text = re.sub(r'(([\s　]+))', '', text)
	return text

database = SqliteExtDatabase('../collocation.sqlite3', autocommit=False, journal_mode='persist')
# database = SqliteExtDatabase('../trigram24000.sqlite3', autocommit=False, journal_mode='persist')
database.connect()
class BaseModel(Model):
    class Meta:
        database = database

class trigram(BaseModel):
    W1 = CharField(null=True)
    W2 = CharField(null=True)
    W3  = CharField(null=True)
    P1  = CharField(null=True)
    P2 = CharField(null=True)
    P3 = CharField(null=True)
    cnt = IntegerField(null=True)
    ok = IntegerField(null=True)
    ng = IntegerField(null=True)
    class Meta:
        db_table = 'trigram'

class mSentence(BaseModel):
	framework = CharField(null=True)
	cnt = IntegerField(null=True)
	ok = IntegerField(null=True)
	ng = IntegerField(null=True)
	class Meta:
		db_table = 'meta_sentence'

class collocation(BaseModel):
	word1 = CharField(null=True)
	word2 = CharField(null=True)
	genkei1 = CharField(null=True)
	genkei2 = CharField(null=True)
	hinshi1 = CharField(null=True)
	hinshi2 = CharField(null=True)
	cnt = IntegerField(null=True)
	ok = IntegerField(null=True)
	ng = IntegerField(null=True)
	class Meta:
		db_table = 'collocation'

def get_twlog_list(n = 1000, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308']):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			if UserList == []:
				tweets = Tweets.select().where(~Tweets.text.contains('RT'), ~Tweets.screen_name << BlackList, ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
			else:
				tweets = Tweets.select().where(Tweets.screen_name << UserList , ~Tweets.screen_name << BlackList, ~Tweets.text.contains('RT'), ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [clean_text(tweet.text) for tweet in tweets  if 'RT' not in tweet.text]
			return tweetslist
	except Exception as e:
		db.rollback()
		# print(e)

def getTrigram(startWith = '', Plist = ['<BOS>','名詞','名詞','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], endWithList = ['。', '!', '！', '?', '？'], is_debug = False, n = 50):
	QuestionPhrase = '<KEY>...？'
	if startWith != '':
		ans = ['<BOS>', startWith]
	else:
		ans = ['<BOS>']
	# print(Plist)
	lenP = len(Plist)
	i = 0
	isNext = True
	try:
		with database.transaction():
			if len(ans) == 1:
				try:
					Ws = trigram.select().where(trigram.W1 == ans[0], trigram.P2 == Plist[1]).order_by(trigram.cnt.desc())
					W = np.random.choice([w.W2 for w in Ws])
				except Exception as e:
					W = ''
				ans.append(W)
				# print(ans)
			while(True):
				isNext = True
				pre1 = ans[i]
				pre2 = ans[i+1]
				P3 = Plist[i+2]
				P2 = Plist[i+1]
				P1 = Plist[i]
				if isNext:
					# print('2単語一致前方2品詞一致', ans, i)
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2, trigram.P1 == P1).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext: 
					# print('2単語一致前方1品詞一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3, trigram.P2 == P2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('2単語一致品詞一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2, trigram.P3 == P3).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('2単語一致')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1, trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('1単語一致')
					try:
						Ws = trigram.select().where(trigram.W2 == pre2).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W3 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						isNext = True
				if isNext:
					# print('1単語一致2')
					try:
						Ws = trigram.select().where(trigram.W1 == pre1).order_by(trigram.cnt.desc()).limit(n)
						W = np.random.choice([w.W2 for w in Ws])#, p = [w.cnt for w in Ws])
						isNext = False
					except Exception as e:
						if i == 0:
							return QuestionPhrase.replace('<KEY>', pre2)
						isNext = True
				ans.append(W)
				if is_debug:
					print(ans)
				i = i +1
				if lenP < i+3:
					break
				if W == '<EOS>':
					break
				if W in endWithList:
					break
				if i > 30:
					break
				W = ''
	except Exception as e:
		database.rollback()
		# print(e)
	return ''.join(ans)

def saveCollocation(tri):
	try:
		ma1 = tri[0]
		ma2 = tri[1]
		ma3 = tri[2]
		database.create_tables([trigram, mSentence], True)
		with database.transaction():
			try:
				T, created = trigram.get_or_create(W1 = ma1[0], W2 = ma2[0], W3 = ma3[0], P1 = ma1[1], P2 = ma2[1], P3 = ma1[1])
				if created == True:
					T.W1 = ma1[0]
					T.W2 = ma2[0]
					T.W3  = ma3[0]
					T.P1  = ma1[1]
					T.P2 = ma2[1]
					T.P3 = ma3[1]
					T.cnt = 1
					T.save()
				else:
					T.cnt = T.cnt +1
					T.save()
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()
		# print(e)

def saveCol(P):
	Pstr = ','.join(P)
	try:
		database.create_tables([trigram, mSentence, collocation], True)
		with database.transaction():
			try:
				M, created = collocation.get_or_create(framework = Pstr)
				if created == True:
					M.cnt = 1
					M.ok = 1
					M.ng = 0
					M.save()
				else:
					M.cnt = M.cnt +1
					M.save()
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()

def TrigramCore(s, is_learn = False, is_debug = False):
	s = s.replace('海未', '園田海未').replace('うみちゃん', '園田海未').replace('穂乃果', '高坂穂乃果').replace('ほのか', '高坂穂乃果').replace('かよちん', '小泉花陽')
	ma = natural_language_processing.MA.get_mecab_coupled(s)
	ma = [[w[0], w[1]] for w in ma]
	ma = [['<BOS>', '<BOS>']] + ma + [['<EOS>', '<EOS>']]
	Plist = [w[1] for w in ma]
	saveMetaS(Plist)
	wcnt = len(ma)
	triMA = [[ma[i], ma[i+1], ma[i+2]] for i in range(wcnt-2)]
	if is_learn:
		[saveTrigram(ma) for ma in triMA]
	if is_debug:
		print(triMA)

def learnTrigram(sList):
	i = 1;
	for s in sList:
		print('++++++++++++++++++++++++++++++++++++++++++++++++++')
		print(i, s)
		try:
			mas = TrigramCore(s, 1, 1)
		except Exception as e:
			print('')
		i += 1

def learnLang(sList):
	i = 1;
	for s in sList:
		print('++++++++++++++++++++++++++++++++++++++++++++++++++')
		print(i, s)
		try:
			trigram = TrigramCore(s, 1, 0)
			tfidf = TFIDF.TFIDF(s, i, True, 0)
		except Exception as e:
			print('')
		i += 1

def extractKeywords(ma, exp = ['助詞', '助動詞', '記号', '接続詞', '数']):
	def isKeyword(x, exp = ['助詞', '助動詞', '記号', '接続詞', '数']):
		if x[1] in exp:
			return False
		elif x[2] in exp:
			return False
		else:
			return True
	return [x for x in sorted(ma, key = lambda x: x[10], reverse = True) if isKeyword(x, exp)]

def getMetaSentence(n = 50):
	try:
		# database.create_tables([trigram, mSentence], True)
		with database.transaction():
			try:
				Ms = mSentence.select().where(mSentence.framework.contains('<BOS>,名詞,')).order_by(mSentence.cnt.desc()).limit(n)
				return np.random.choice([m.framework for m in Ms])#, p = [m.cnt for m in Ms])
			except Exception as e:
				print('')
			database.commit()
	except Exception as e:
		database.rollback()
		print(e)

from sklearn.cluster import KMeans
def kmeans(features, k=10):
    km = KMeans(n_clusters=k, init='k-means++', n_init=1, verbose=True)
    km.fit(features)
    return km.labels_
def plot(features, labels):
    import matplotlib.pyplot as plt
    plt.scatter(features[:, 0], features[:, 1], c=labels, cmap=plt.cm.jet)
    plt.show()

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
def main(items, isPlot =False):
    vectorizer = TfidfVectorizer(
        use_idf=True
    )
    X = vectorizer.fit_transform(items)
    lsa = TruncatedSVD(10)
    X = lsa.fit_transform(X)
    X = Normalizer(copy=False).fit_transform(X)
    km = KMeans(init='k-means++',)
    km.fit(X)
    kmlabel = km.labels_
    print(kmlabel)
    labeled_items = [(kmlabel[i], items[i]) for i in range(len(kmlabel))]
    labelcnt = len(kmlabel)
    i =0
    while(True):
    	print('++++++++++++++++++')
    	print('クラスタNo.', i)
    	[print('・', item[1]) for item in labeled_items if item[0] == i]
    	i += 1
    	if i > labelcnt:
    		break
    if isPlot:
    	plot(X, km.labels_)

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	import TFIDF
	try:
		argvs = sys.argv
		intext = argvs[1]
		command = argvs[2]
	except:
		command = ''
		intext = ''''''
	features = np.random.rand(512, 2)
	k = 10
	labels = kmeans(features, k=k)
	# plot(features, labels)

	tweetslist = get_twlog_list(10000, [])
	items = [' '.join([w[0] for w in natural_language_processing.MA.get_mecab_coupled(tweet) if w[1] in ['名詞', '動詞', '形容詞', '固有名詞']]) for tweet in tweetslist]

	main(items, isPlot = True)
