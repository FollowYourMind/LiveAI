# -*- coding: utf-8 -*-
# from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import TruncatedSVD
from sklearn import datasets
from sklearn.cross_validation import cross_val_score
import natural_language_processing
from gensim import corpora, matutils
import re
import numpy as np
from itertools import chain
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase


db = SqliteExtDatabase('../Data/twtrData.sqlite3', autocommit=False, journal_mode='persist')
db.connect()
class TBaseModel(Model):
    class Meta:
        database = db
class Tweets(TBaseModel):
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

def get_twlog_list(n = 1000):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():# and Tweets.text.contains('怒')
			tweets = Tweets.select().where(Tweets.screen_name << ['FootUse'] and ~Tweets.text.contains('RT')).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [clean_text(tweet.text) for tweet in tweets]
			return tweetslist
	except Exception as e:
		db.rollback()
		# print(e)

sList = ['全然だめだ。', 'まったく回答になっていない。', 'よくできたね。', 'えらいえらい', 'だめだ']
label_train = [1,1, 0, 0, 1]
# sList = get_twlog_list(10)
print(sList)
maList = [natural_language_processing.MA.get_mecab(s, mode = 7, form = ['名詞', '形容詞','副詞', '動詞'], exception = ["記号"], is_debug = False) for s in sList]
# words はさっきの単語リスト
dictionary = corpora.Dictionary(maList)
# dictionary.filter_extremes(no_below=20, no_above=0.3)
print(dictionary.token2id)

diclen = len(dictionary)

tmps = [dictionary.doc2bow(ma) for ma in maList]
data_train = [matutils.corpus2dense([tmp], num_terms = diclen).T[0] for tmp in tmps]
print(data_train)
# print(labels)
#特徴量の次元を圧縮
#似たような性質の特徴を同じものとして扱います
# lsa = TruncatedSVD(2)
# reduced_features = lsa.fit_transform(features)
# estimator = RandomForestClassifier()
# estimator.fit(data_train, label_train)
# 予測
data_test = get_twlog_list(10)
print(data_test)
# label_predict = estimator.predict(data_test)
# print(label_predict)
# print(reduced_features)
# clf_names = ["RandomForestClassifier"]
# for clf_name in clf_names:
#   clf    = eval("%s()" % clf_name) 
#   scores = cross_val_score(clf,reduced_features, labels,cv=5)
#   score  = sum(scores) / len(scores)  #モデルの正解率を計測
#   print ("%sのスコア:%s" % (clf_name,score))

