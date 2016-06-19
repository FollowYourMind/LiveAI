#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
##______________________
## CaboChaによる構文解析 //
import CaboCha
class SyntacticAnalysis:#CaboCha
    def getWords(self,tree, chunk):
        surface=""
        for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size):
            token = tree.token(i)
            features = token.feature.split(',')
            if features[0] == '名詞':
                surface += token.surface
            elif features[0] == '形容詞':
                surface += features[6]
                break
            elif features[0] == '動詞':
                surface += features[6]
                break
        return surface

    def getTree(self,sentence):
        c=CaboCha.Parser()
        tree=c.parse(sentence)
        print(tree.toString(CaboCha.FORMAT_TREE))

    def cmdCaboCha(self, s):
        command= 'echo %s | cabocha'%(s)
        ret = subprocess.check_output(command, shell=True)
        ret = ret.decode('utf-8')
        ret = ret.replace('\t',',')
        ret = ret.split('\n')
        return ret

    def getRelation(self,line):
        cp = CaboCha.Parser('-form')
        # tree = self.cmdCaboCha(line)
        tree = cp.parse(line)
        chunk_dic = {}
        chunk_id = 0
        for i in range(0, tree.size()):
            token = tree.token(i)
            if token.chunk:
                chunk_dic[chunk_id] = token.chunk
                chunk_id += 1
        tuples = []
        for chunk_id, chunk in chunk_dic.items():
            if chunk.link > 0:
                from_surface =  self.getWords(tree, chunk)
                to_chunk = chunk_dic[chunk.link]
                to_surface = self.getWords(tree, to_chunk)
                tuples.append((from_surface, to_surface))
        return tuples

    def getTuples(self,sentence):
        tuples=self.getRelation(sentence)
        return tuples

    def showPairs(self,sentence):
        SyA_tuples=self.getTuples(sentence)
        for t in  SyA_tuples:
            print(t[0] + ' => ' + t[1])

SyA=SyntacticAnalysis()
if __name__ == '__main__':
	import sys
	import io
	import os
	argvs = sys.argv
	p1 = argvs[1]
	p2 = argvs[2]
	if p2 ==  'SyA.getTree()':
		result = SyA.getTree(p1)
	else:
		result = SyA.showPairs(p1)
	print(result)












