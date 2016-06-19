#!/usr/bin/env python
# -*- coding: utf-8 -*-
##______________________
## MeCabによる形態素解析 //
# import MeCab
import subprocess
import re

def Kaomoji(s):
    text = '[0-9A-Za-zぁ-ヶ一-龠]';
    non_text = '[^0-9A-Za-zぁ-ヶ一-龠]';
    allow_text = '[ovっつ゜ニノ三二]';
    hw_kana = '[ｦ-ﾟ]';
    open_branket = '[\(∩꒰（]';
    close_branket = '[\)∩꒱）]';
    arround_face = '(?:' + non_text + '|' + allow_text + ')*';
    face = '(?!(?:' + text + '|' + hw_kana + '){3,}).{3,}';
    face_char = re.compile(arround_face + open_branket + face + close_branket + arround_face);
    facelist = face_char.findall(s)
    cleaned = re.sub(face_char, '(^ ^)' , s)
    return cleaned, facelist

class MorphologicalAnalysis:#MeCab
    #OLD
    def get_morpho(self,sentence):
        text = MeCab.Tagger("-Owakati")
        node = text.parse(sentence)
        result = node.rstrip(" \n").split(" ")
        return result
    def get_genkei2(self, sentence,Debug=False):
        print("Please up to date get_katakana() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="-g",form="動詞,名詞,副詞,形容詞",exception="",returnstyle="tuple",Debug=Debug)
    def get_katakana(self, sentence,Debug=False):
        print("Please up to date get_katakana() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="-k",form="",exception="",returnstyle="tuple",Debug=Debug)
    def get_noun(self, sentence):
        print("Please up to date get_noun() to getMeCab()")
        return self.getMeCab(sentence=sentence,mode="",form="",exception="",returnstyle="tuple",Debug=Debug)
        
    def cmdMeCab(self, s):
        try:
            MECAB = '/usr/local/bin/mecab'
            # MECAB = '/usr/bin/mecab'
            DIC = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
            s = s.replace('\n','').replace('(','').replace(')','')
            cmd= 'echo %s | %s -d %s'%(s, MECAB, DIC)
            p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_data, stderr_data = p.communicate()
            ret = stdout_data
            ret = ret.decode('utf-8')
            ret = ret.replace('\t',',')
            ret = ret.split('\n')
            return ret
        except:
            return ''
    def splitMeCab(self, info):
        ma = info.split(',')
        length = len(ma)
        if length != 10:
            for x in range(10 - length):
                ma.append('*')
        if ma[7] == '*':
            ma[7] = ma[0]
        return ma

    def get_mecab_ls(self, sentence):
        cleanedS, Face = Kaomoji(sentence)
        info_of_words = self.cmdMeCab(cleanedS)
        maList = [self.splitMeCab(info) for info in info_of_words if not info in ['EOS', '']]
        if Face != []:
            Face0 =  Face[0]
            Kao =  [Face0, '記号', '顔文字', '*', '*', '*', '*', Face0, 'カオ', 'カオ']
            maList = [ma if not ma[0] == '^ ^' else Kao for ma in maList]
        return maList

    #Main     OLD
    def getMeCab(self, sentence, mode = "-g", listForm = [""], listException = ["記号"], returnstyle = "tuple", Debug = False):
        try:
            #原文のscreening
            sentence = sentence.replace("\u3000","").replace("\t",",")
            #MeCabモジュールなしで。
            info_of_words = self.cmdMeCab(sentence)
            # print(info_of_words)

            # modeセレクト
            mode_name, modenum = self.selectMeCabMode(mode=mode)
            #複数指定対応
            isExceptionOK = False
            words = []
            info_elems = self.get_mecab_ls(sentence)
            # for info in info_of_words:
            #     if info == 'EOS' or info == '': 
            #         break
            #     info_elems = info.split(',')
                if form == "":
                    signalForm = True
                else:
                    signalForm = False
                    for form in listForm:
                        for i in range(7):
                            if info_elems[i] == form:
                                signalForm = True
                                break

                #exception_list=["数","接尾","非自立","自立","接続助詞","格助詞","代名詞"]
                isExceptionOK=True
                if exception!="":
                    for exp in listException:
                        for i in range(7):
                            if info_elems[i] == exp: #source_type
                                isExceptionOK = False
                                break

                if signalForm==True:
                    if info_elems[7] == '*':
                        words.append(info_elems[0][:2])
                    if isExceptionOK==True:
                        try:
                            words.append(info_elems[modenum])
                        except:
                            words.append(info_elems[0])
                if Debug==True:
                    print(info_elems)
            # return ma
            if Debug==True:
                print("[Debug] mode:"+mode_name)
                print(words)

    #スクリーニング
            words = self.removeEmpty([w.replace('*','') for w in words])
    #吐き出すstyleを指定
            ans = self.changeStyle(words=words,style=returnstyle)
            return ans
        except:
            # print('KeyError')
            return ''

    def selectMeCabMode(self, mode):
        if mode=="-g"or mode=="7":
            mode_name="原型"
            modenum=7
        elif mode == "-k" or mode == "8":
            mode_name = "カタカナ"
            modenum = 8
        elif mode == '0':
            mode_name="Raw"
            modenum = 0
        else:
            try:
                mode_name = mode
                modenum = int(mode)
            except:
                mode_name = "Raw"
                modenum = 0
        return mode_name, modenum

    def split2List(self, s, parser = ','):
        if parser in s:
            sList = s.split(parser)
        else: 
            sList = [s]
        return sList

    def changeStyle(self, words, style = 'tuple'):
        if style=="tuple":
            return tuple(words)
        elif style=="list":
            return words
        else: return("Error:return style")

    def removeEmpty(self, list):
        while (True):
            try:
                list.remove("")
            except:
                break
        return list

MA = MorphologicalAnalysis()

## ______________________
## CaboChaによる構文解析 //
# import CaboCha
# class SyntacticAnalysis:#CaboCha
#     def getWords(self,tree, chunk):
#         surface=""
#         for i in range(chunk.token_pos, chunk.token_pos + chunk.token_size):
#             token = tree.token(i)
#             features = token.feature.split(',')
#             if features[0] == '名詞':
#                 surface += token.surface
#             elif features[0] == '形容詞':
#                 surface += features[6]
#                 break
#             elif features[0] == '動詞':
#                 surface += features[6]
#                 break
#         return surface

#     def getTree(self,sentence):
#         c=CaboCha.Parser()
#         tree=c.parse(sentence)
#         print(tree.toString(CaboCha.FORMAT_TREE))

#     def cmdCaboCha(self, s):
#         command= 'echo %s | cabocha'%(s)
#         ret = subprocess.check_output(command, shell=True)
#         ret = ret.decode('utf-8')
#         ret = ret.replace('\t',',')
#         ret = ret.split('\n')
#         return ret

#     def getRelation(self,line):
#         cp = CaboCha.Parser('-form')
#         tree = cp.parse(line)
#         chunk_dic = {}
#         chunk_id = 0
#         for i in range(0, tree.size()):
#             token = tree.token(i)
#             if token.chunk:
#                 chunk_dic[chunk_id] = token.chunk
#                 chunk_id += 1
#         tuples = []
#         for chunk_id, chunk in chunk_dic.items():
#             if chunk.link > 0:
#                 from_surface =  self.getWords(tree, chunk)
#                 to_chunk = chunk_dic[chunk.link]
#                 to_surface = self.getWords(tree, to_chunk)
#                 tuples.append((from_surface, to_surface))
#         return tuples

#     def showPairs(self,sentence):
#         SyA_tuples=self.getTuples(sentence)
#         for t in  SyA_tuples:
#             print(t[0] + ' => ' + t[1])

#     def getTuples(self,sentence):
#         tuples=self.getRelation(sentence)
#         return tuples
# SyA=SyntacticAnalysis()

# ##______________________
# ## npjadicによる感情分析 //
# import npjadic
# class SentimentAnalysis:
#     def makeDic(self):
#         dic=npjadic.dic
#         dic=dic.replace("\n",":")
#         nplist=dic.split(':')
#         i=0
#         wordslist=[]
#         valuelist=[]
#         for i in range(len(nplist)):
#             if i%4==1:
#                 wordslist.append(nplist[i])
#             if i%4==2:
#                 wordslist.append(nplist[i])
#             if i%4==0:
#                 valuelist.append(nplist[i])
#                 valuelist.append(nplist[i])
#         NPdic=dict(zip(wordslist,valuelist))
#         return NPdic

#     def getNPscore(self,text,Debug=False):
#         # print(NPdic[0])
#         NPdic=self.makeDic()
#         word=MA.getMeCab(sentence=text,mode="-g",form="動詞,名詞,形容詞,副詞"  ,exception="",returnstyle="tuple",Debug=True)
#         #exception="非自立,助詞類接続,サ変・スル"
#         if Debug==True:
#             print(word)
#         i=0
#         sumscore=0
#         for i in range(len(word)):
#             if word[i] in NPdic:
#                 score=NPdic[word[i]]
#                 if Debug==True:
#                     print(word[i]+":"+score)
#                 sumscore+=round(float(score),8)
#                 sumscore=round(sumscore,8)
#             i+=1
#         ansscore=round(sumscore,8)
#         if Debug==True:
#             print("NPScore:"+str(ansscore))
#         return(ansscore)
# SeA=SentimentAnalysis()

if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    s= "レスポンシビリティカールフォンクラウゼヴィッツご注文はうさぎですか?の戦略論"
    # s = 'ごちうさがみたいんじゃ'
    nouns = MA.get_mecab_ls(s)
    print(nouns)



