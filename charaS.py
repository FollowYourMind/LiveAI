#!/usr/bin/env python
# -*- coding: utf-8 -*-
##______________________
## MeCabによる形態素解析 //
# import MeCab
import subprocess
import re
from itertools import chain
import numpy as np
import natural_language_processing
def multiple_replace(text, adict):
    """ 一度に複数のパターンを置換する関数
    - text中からディクショナリのキーに合致する文字列を探し、対応の値で置換して返す
    - キーでは、正規表現を置換前文字列とできる
    """
    rx = re.compile('|'.join(adict))
    def dedictkey(text):
        for key in adict.keys():
            if re.search(key, text):
                return key
    def one_xlat(match):
        return adict[dedictkey(match.group(0))]
    return rx.sub(one_xlat, text)

def conjugate(w, style = '終止形'):
    #//未然連用終止連体仮定命令 6(未ウ), 7(連タ)
   conjuTable = {
        '五段・カ行促音便': ['か','き', 'く', 'く', 'け', 'け', 'こ', 'っ'],
        '五段・カ行イ音便': ['か','き', 'く', 'く', 'け', 'け', 'こ', 'い'],
        '五段・ガ行': ['が','ぎ', 'ぐ', 'ぐ', 'げ', 'げ', 'ご', 'い'],
        '五段・サ行': ['さ','し', 'す', 'す', 'せ', 'せ', 'そ', 'し'],
        '五段・タ行': ['た','ち', 'つ', 'つ', 'て', 'て', 'と', 'っ'],
        '五段・ナ行': ['な','に', 'ぬ', 'ぬ', 'ね', 'ね', 'の', 'ん'],
        '五段・バ行': ['ば','び', 'ぶ', 'ぶ', 'べ', 'べ', 'ぼ', 'ん'],
        '五段・マ行': ['ま','み', 'む', 'む', 'め', 'め', 'も', 'ん'],
        '五段・ラ行': ['ら','り', 'る', 'る', 'れ', 'れ', 'ろ', 'っ'],
        '五段・ラ行特殊': ['ら', 'い', 'る', 'る', 'れ', 'れ', 'ろ', 'っ'],
        '五段・ワ行促音便': ['わ','い', 'う', 'う', 'え', 'え', 'を', 'っ'],
        '五段・ワ行イ音便': ['わ','い', 'う', 'う', 'え', 'え', 'を'],
        '五段・ワ行ウ音便': ['わ','い', 'う', 'う', 'え', 'え', 'を', 'ふ'],
        '一段':  ['', '', 'る', 'る', 'れ', 'ろ', '', ''],
        '一段・クレル': ['れる', 'れ', 'れ', 'れれ', 'れ', 'れよ', 'れ'],
        'カ変・来ル': ['来','来', '来る', '来る', '来れ', '来い','','来'],
        'カ変・クル': ['こ','き', 'くる', 'くる', 'くれ', 'こい','','き'],
        'サ変・スル': ['し','し', 'する', 'する', 'すれ', 'すれ', '', 'し'],
        '形容詞・イ段': ['かろ', 'く', 'い', 'い', 'けれ', '', '', 'く'],
        '形容詞・アウオ段': ['かろ', 'かっ', 'い', 'い', 'けれ', '', '', 'く'],
        '形容詞・イイ': ['い', 'い', 'い', 'い', 'い', 'い', 'いっ', 'い'],
        '特殊・ナイ': ['なかろ', 'なく', 'ない', 'ない', 'なけれ', '', 'なかっ'],
        '特殊・タイ': ['たかろ', 'たく', 'たい', 'たい', 'たけれ', '', 'たかっ'],
        '特殊・デス': ['でしょ', 'でし', 'です', 'です', '', '', 'でしょ', 'でし'],
        '特殊・マス': ['ませ', 'まし', 'ます', 'ます', 'ますれ', 'ませ', 'ましょ', 'まし'],
        '特殊・タ': ['たろ', '', 'た', 'た', 'たら', '', 'たろ', ''],
        '特殊・ダ': ['だろ', 'で', 'だ', 'な', 'なら', '', 'だろ', 'だっ'],
        '特殊・ヤ': ['やろ', 'やっ', 'や', 'な', 'なら', '', 'やろ', 'やっ'],
        '*': None
    }
   conjuType = w[5]
   g = w[7]
   if conjuType in {'サ変・スル', 'カ変・来ル', 'カ変・クル'}:
      gokan = ''
   else:
      gokan = g[:-1]
   conjuArray = conjuTable[conjuType]
   if conjuArray is None:
      # conjuArray = [g, g, g, g,g ,g, g, g]
      conjuArray = g *7
   p(conjuArray)
   w1 = w[1]
   if w1 in ['動詞', '形容詞']:
      if style in ['未然レル接続']:
          if w[5] == 'サ変・スル':
              return 'さ'
          else:
              return gokan + conjuArray[0]
      elif style == '未然形':
          return gokan + conjuArray[0]
      elif style == '連用形':
          return gokan +conjuArray[1]
      elif style in ['基本形', '終止形']:
          return gokan + conjuArray[2]
      elif style in ['連体形']:
          return gokan + conjuArray[3]
      elif style in ['仮定形']:
          return gokan + conjuArray[4]
      elif '命令' in style:
          return gokan + conjuArray[5]
      elif style == '未然ウ接続':
          return gokan + conjuArray[6]
      elif style in ['連用タ接続', '連用テ接続']:
          return gokan + conjuArray[7]
      elif style in ['ガル接続', '連用ゴザイ接続']:
          return gokan
      else:
          return 'ERR'
   elif w1 in ['助詞', '助動詞語幹']:
      return w[0]
   elif w1 in ['助動詞']:
      if w[5] == '五段・ラ行特殊':
          gokan = gokan
      else:
          gokan = ''
      if style == 'ガル接続':
          return gokan
      elif style == '未然形':
          return gokan + conjuArray[0]
      elif style == '連用形':
          return gokan +conjuArray[1]
      elif style in {'基本形', '終止形'}:
          return gokan + conjuArray[2]
      elif style in {'連体形'}:
          return gokan + conjuArray[3]
      elif style in {'仮定形'}:
          return gokan + conjuArray[4]
      elif '命令' in style:
          return gokan + conjuArray[5]
      elif style == '未然ウ接続':
          return gokan + conjuArray[6]
      elif style in {'連用タ接続', '連用テ接続', '連用ゴザイ接続'}:
          return gokan + conjuArray[7]
      elif style in {'ガル接続'}:
          return gokan
      else:
          return w[0]
   else:
      return w[0]

def conjuMulti(w1, w2):
   try:
      nextHinshi = w2[1];
      nextWordG = w2[7];
      connection = w1[6];
      if nextHinshi == '名詞':
         if connection in set(['連用タ接続', '連用テ接続','ガル接続']):
            return conjugate(w1, connection)
         else:
            return conjugate(w1, '連体形')
      elif nextHinshi == '名詞':
         if connection in set(['未然レル接続', '連用タ接続', '連用テ接続','ガル接続']):
            return conjugate(w1, connection)
         else:
            return conjugate(w1, '連用形')
      if nextHinshi == '助動詞':
         if connection in set(['未然ウ接続', '連用タ接続', '連用テ接続','ガル接続']):
            return conjugate(w1, connection)
         else:
            if nextWordG in set(['れる', 'られる', 'せる', 'させる', 'ない', 'ぬ', 'う', 'よう', 'まい']):
               return conjugate(w1, '未然形')
            elif nextWordG in set(['た', 'たい', 'ます']):
               return conjugate(w1, '連用形')
            elif nextWordG in set(['や', 'やん', 'らしい', 'らし']):
               return conjugate(w1, '基本形')
            else:
               return w1[0]
      elif nextHinshi == '助詞':
         if nextWordG == 'わ':
            return ''.join([w1[0], 'です。'])
         elif nextWordG == 'よ':
            if w1[5] == '特殊・デス':
               return 'です';
            elif '命令' in connection:
               return conjugate(w1, '命令')
            else:
               return conjugate(w1, '基本形')
         elif nextWordG in set(['けど', 'けれど']):
            if w1[5] not in set(['特殊・デス', '特殊・マス']):
               return ''.join([w1[0], 'けど'])
            else:
               return  w1[0] + 'けど'
         else:
            return w1[0]
      else:
         return w1[0]
   except Exception as e:
      # print(e)
      return  w1[0]

def umiChar(s):
    ma = natural_language_processing.MA.get_mecab_coupled(s)
    wcnt = len(ma)
    umiMap = {
        # // タグ変換
        '<形容動詞語幹接尾>': '的',
        '<一般接尾>': 'よう',
        'だ<Nya>' : 'です。',
        '<Nya>': '',
        # // ごみ取り
        '。。': '。',
        'RT': '',
        'ww': '(笑)',
        'www': '',
        'undefined': '',
        'ふるぁぼ': 'ふぁぼ',
        # //終助詞変換
        'たです': 'たのです。',
        'たぜ': 'たのです。',
        'わね': 'ですね。',
        'わよ': 'ですよ',
        'のよ': 'のですか',
        'たにゃ': 'です。',
        'かにゃ': 'ですか。',
        'かしら': 'ですか。',
        'するゾ': 'しますよ。',
        'ｽｷﾞｨ': 'すぎです。',
        'スギィ': 'すぎです。',
        'っすか': 'ですか',
        'よな': 'ですよね',
        'んだよ': 'んですよ',
        'だぞ': 'ですよ',
        'くるです': 'くるのです。',
        'なぁです': 'です。',
        'ねぇ': 'ね♪',
        'かな。': 'ですかね♪',
        'ですかねえ': 'ですかね♪',
        # //名詞変換
        '俺': '私',
        'オレ': '私',
        'おれ': '私',
        'お前': 'あなた',
        'おまえ': 'あなた',
        'クソ': '',
        'くそ': '',
        'ちっこい': '小さい',
        'ぶち込んで': '入れて',
        'すげるぇ': 'すごい',
        # //ラ！固有名詞変換
        '海ちゃん': '海未',
        'うみちゃん': '私',
        '海未ちゃん': '私',
        'うみまく': '海未真姫',
        # // めんどいバグ放置
        'けどけど': 'けれど',
        '死ねで': '死んで',
        '寝う': '寝よう',
        'ですかですよ。': 'ですか。',
        'なかっよ': 'なかったよ',
        'でみう': 'でみよう',
        'てみう': 'てみよう',
        'だです。': 'です。',
        'やけれど': 'ですけど',
        'おつかれるさま': 'おつかれさま'
    };
    return multiple_replace(s, umiMap)
def convertNoun(w, tail = 'です'):
   detailHinshi = w[2]
   return ''.join([w[0], tail])

def dealTrigram(ma, i):
   w1 = ma[i-1]
   w2 = ma[i]
   w3 = ma[i+1]
   # print(w1, w2, w3)
   w2w = w2[0]
   w21 = w2[1]
   if i == 0:
      if w21 == '名詞':
         return convertNoun(w2, '')
      elif w21 == '副詞':
         adv = w2[7]
         if adv in set(['にゃー','にゃん']):
            return '<Nya>'
         else:
            return w2w
      elif w21 == '記号':
         return '...'
      return w2w
   elif i != len(ma)-2:
      if w21 in set(['動詞', '形容詞']):
         return conjuMulti(w2, w3)
      elif w21 == '助動詞':
         if w2[6] == 'ガル接続':
            return 'た'
         elif w2[0] == 'たら':
            return 'たら'
         else:
            return conjuMulti(w2, w3)
      elif w21 == '名詞':
         return convertNoun(w2, '')
      elif w21 in set(['副詞', '助詞', '終助詞']):
         adv = w2[7]
         if adv in set(['にゃー','にゃん', 'にゃ']):
            return '<Nya>'
         else:
            return w2w
      else:
         return w2w
   else:
      if w21 == '動詞':
         if w1[7] != 'くださる':
            return conjugate(w2, '連用テ接続') + 'てくださいね。'
         else:
            return 'ね。'
      elif w21 == '形容詞':
         return conjugate(w2, '基本形') + 'です。'
      elif w21 == '名詞':
         return convertNoun(w2, 'ですよ。')
      elif w21 == '助動詞':
         w25 = w2[5]
         if w21 in  set(['特殊・デス', '特殊・ダ']):
            return 'です♪';
         elif w21 == '特殊・マス':
            return 'ます♪';
         else:
            if w2[7] == 'ん':
               return 'んか？？'
            else:
               return conjugate(w2, '基本形') + 'です。'  
      elif w21 == '副詞':
         adv = w2[7];
         if adv in set(['にゃー','にゃん', 'にゃ']):
            return '<Nya>'
         else:
            return w2w
      elif w21 == '終助詞':
         if w2w == 'な':
            if w1[1] == '形容詞':
                return 'ですね。'
            else:
                return 'な。'
         elif w2w == 'か':
            if w1[5] == 'サ変・スル':
                if w1[0] == 'し':
                    return 'ますか？'
                else:
                    return 'のですか？'
            elif w1[5] == '特殊・デス':
                return 'か。'
            else:
                return 'ですか？'
      elif w21 in set(['ぜ', 'よ']):
         if '命令' in w1[6]:
             return 'よ。'
         elif w1[5] == '特殊・ダ':
             return 'すよ'
         else:
             return 'よ'
      elif '助詞' in w21:
         if w2[2] in set(['特殊', '接続助詞']):
             return '...'
      else:
         return w2[0]
    # ansList.push('<EOS>')
    # charS = ansList.join('');
    # return charS
def umiCharMain(s, info = ''):
  FACE = '( •̀ ᴗ •́ )';
  ma = natural_language_processing.MA.get_mecab_coupled(s)
  wcnt = len(ma)
  result = [result for result in [dealTrigram(ma, i) for i in range(wcnt-1)] if result != None]
  return umiChar(''.join(result))
if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    s = '!わたしは44元気だけど。悲しみるにゃーけど言うてくる。しかし、不愉快であるにゃー'
    nouns = umiCharMain(s)
    print(nouns)



