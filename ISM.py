#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import numpy as np
import _
from _ import p, d, MyObject, MyException
##_____________________
## ISM法 //
## 悩み相談をしながら、構造化モデリングで悪構造問題を良構造に変換し、アドバイスを行う。
def f7(seq): ##高速化ver
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def prd_boolen_matrix(matrix):
	products = matrix.dot(matrix)
	# boolean
	products[products > 1] =1
	if products.all() != matrix.all():
		autoproductMatrix(matrix)
	else:
		return products

def npwhere(arr):
	ret = []
	where = np.where(arr)
	where_ls = where[0].tolist()
	ret.append(where_ls)
	return ret[0]

def calcRcapA(R,A,S):
	RcapA = []
	for Si in range(S):
		Ri = R[Si]
		Ai = A[Si]
		RiAi = [aRi for aRi in Ri if aRi in Ai]
		RcapA.append(RiAi)
	# print(RcapA)
	# print(A)
	# set_a = set(A)
	# set_r = set(R)
	# print(set_r.intersection(set_a))
	return RcapA

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]

def identify_level_elements(R,A,structure, is_print):
	# dirtyCode... リスト内包表記で要修正
	p('~~~~~~~~~~~~~~~~~~~~~~~~~~~', is_print = is_print)
	S = len(R)
	strS = str(S)
	Level = []
	structureN = []
	RcapA = calcRcapA(R,A,S)
	p('RcapA',is_print = is_print)
	p(RcapA, is_print = is_print)
	for i in range(S):
		Ri = R[i]
		RiAi = RcapA[i]
		if RiAi == Ri:
			Level.append(Ri)
			if Ri:
				structureN.append(i)
		# try:
	altR = []
	p('Level', is_print = is_print)
	Level = [level for level in Level if level]
	p(Level, is_print = is_print)
	p('structureN', is_print = is_print)
	p(structureN, is_print = is_print)
	avoidLevel = flatten(Level)
	strong_connected_ls = []
	# check discrete or not
	if len(Level) != 1:
		p('parallel cause-effect... ', is_print = is_print)
		for level in Level:
			if len(level) > 1:
				p(level, ' Not Discrete,  Strongly connected...', is_print = is_print)
				strong_connected_ls.append(level)
				Level.remove(level)
	for i in range(S):
		Ri = R[i]
		altRi = [r for r in Ri if r not in avoidLevel]
		altR.append(altRi)
	p('altR', is_print = is_print)
	p(altR,is_print = is_print)
	structure.append(structureN)
	structure = [structure for structure in structure if structure != [] ]
	p('whole_structure', is_print = is_print)
	p(structure, is_print = is_print)
	StrProgress = len(flatten(structure))
	return altR, structure, StrProgress, strong_connected_ls

def ILEloop(R,A,structure, is_print = True):
	cnt = 1
	total_strong_connected_ls = []
	altR, structure, StrProgress, strong_connected_ls = identify_level_elements(R,A,structure, is_print)
	S = len(altR)
	strS = str(S)
	if strong_connected_ls:
		total_strong_connected_ls.append(strong_connected_ls)
	while StrProgress < S:
		if cnt > 50:
			p('error cnt over', is_print = is_print)
			return structure.append('ERR')
		else:
			p('continue... progress >> ', StrProgress, '/', strS, ' cnt', cnt, is_print = is_print)
			cnt += 1
			altR, structure, StrProgress, strong_connected_ls = identify_level_elements(altR,A,structure, is_print)
			if strong_connected_ls:
				total_strong_connected_ls.append(strong_connected_ls)
	else:
		p('Finished !! ', StrProgress, '/', strS, is_print = is_print)
		p('strong-connect-pair: ', total_strong_connected_ls)
		p(structure)
	return structure

def splitfunc(chunk):
	return chunk.split('\n')

from itertools import chain

def simplifyC(text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5', arrow = '→', is_print  = True):
	chunk = text.split('\n')
	pairs = [arg.split(arrow) for arg in chunk]
	words = list(chain.from_iterable(pairs))
	# print(words)
	factors = f7(words)
	factors_cnt = len(factors)
	p('抽出された要素は以下の通りです。', is_print = is_print)
	p(factors, is_print = is_print)
	z = np.zeros((factors_cnt,factors_cnt))
	I = np.identity(factors_cnt)
	
	causels = [pair[0] for pair in pairs]
	effectls = [pair[1] for pair in pairs]
	causeN = [factors.index(cause) for cause in causels]
	effectN = [factors.index(effect) for effect in effectls]
	z[causeN, effectN] = 1
	adjacency_matrix = z
	reach_ability_matrix = adjacency_matrix + I
	# Identifying process of the 1st level lements
	R = []
	A = []
	p('boolean演算を実行します。', is_print = is_print)
	RAM = prd_boolen_matrix(reach_ability_matrix)
	p('boolにおいて(A+I)^r = (A+I)^(r+1) /= A+I \nとなる可到達行列は以下のとおりです。', is_print = is_print)
	p(RAM, is_print = is_print)
	for Si in range(factors_cnt):
		Ai = RAM[:,Si]
		Ri = RAM[Si]
		A.append(npwhere(Ai))
		R.append(npwhere(Ri))

	p('行列から抽出した集合は以下のとおりです。', is_print = is_print)
	p('A', is_print = is_print)
	p(A, is_print = is_print)
	p('R', is_print = is_print)
	p(R, is_print = is_print)
	structure = []
	Level = []
	structure = ILEloop(R, A, structure, is_print = is_print)
	
	p(structure, is_print = is_print)
	structureName = []
	p('++++result structure is as following !!++++', is_print = is_print)
	ans_ls = []
	ans_ls.append('######EFFECT######')
	for level in structure: 
		level_name = []
		for num in level: 
			level_name.append(factors[num])
		ans_ls.append('↑↑↑↑↑↑↑')
		[ans_ls.append(name) for name in level_name]
		structureName.append(level_name)
	ans_ls.append('######CAUSE######')
	ans = '\n'.join(ans_ls)
	p(ans)
	return structureName, structure
if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		text = argvs[1]
		p2 = argvs[2]
		mode = 'simple'
	except:
		text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5'
		p2 = 'ISM.detail()'
		mode = 'simple'
	# if text == 'demo':
	text = 'S1→S5\nS2→S1\nS2→S3\nS2→S4\nS3→S5\nS3→S4\nS4→S3\nS6→S2\nS6→S5'
	# if p2 == 'ISM.detail()':
	# 	mode = 'detail'
	arrow = '→'
	structure_name, structure = simplifyC(text, arrow, is_print = True)
	p(structure_name)














