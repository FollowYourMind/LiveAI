#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sqlite3
from peewee import *
from datetime import date
db = SqliteDatabase('/Users/masa/Dropbox/Project/umiA/umiA.sqlite3')

class UnknownField(object):
    pass

class Words(Model):
	word = CharField(primary_key=True)
	yomi = CharField(null=True)
	head = CharField(null=True)
	tail = CharField(null=True)
	length = IntegerField(null=True)
	class Meta:
		database =  db
db.connect()

try:
	# 第二引数がTrueの場合、存在している場合は、作成しない
	db.create_tables([Words], True)
	with db.transaction():
		word = {}
		word['word'] = 'もろへいや'
		word['yomi'] = 'アシカガnew'
		word['head'] = 'ア'
		word['tail'] = 'ガ'
		word['length'] = 4
		try:
			w, created = Words.create_or_get(word = word['word'], yomi = word['yomi'], head = word['head'], tail = word['tail'], length = word['length'])
			print(created)
			if created == False:
				w.word = word['word']
				w.yomi = word['yomi']
				w.head =word['head']
				w.tail = word['tail']
				w.length =word['length']
				w.save()
		except Exception as e:
			print(e)
		print(w.yomi)

		try:
			w = Words.get()
		except Exception as e:
			print(e)
			w = None
		print(w.word)

		# User.select().where(User.active == True).order_by(User.username)
		# for word in Words.select():
		# 	print (word.word)
		db.commit()
except IntegrityError as ex:
    print (ex)
    db.rollback()

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')