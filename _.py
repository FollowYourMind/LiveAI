#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from setup import *
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
def p(*elements, is_print = True):
    if is_print:
      pprint.pprint(elements)
def d(*elements):
    logger.debug(elements)
class MyObject(object):
    def __len__(self):
        return len(self.__dict__)
    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)
    def __iter__(self):
        return self.__dict__.iteritems()
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, value):
        self.__dict__[key] = value
    def is_in(self, key):
      return key in dir(self)
class MyException(Exception): pass
def get_thispath():
  return os.path.abspath(os.path.dirname(__file__))
def get_projectpath():
  thispath = get_thispath()
  return '/'.join(thispath.split('/')[:-1])
def getJSON(place, backup_place = None):
  p('old_method_getJSON')
  return get_json(place)

def saveJSON(tmp, place, backup_place = None):
  p('old_method_saveJSON')
  return save_json(tmp, place = place)

def get_json(place, backup_place = None):
  try:
    with open(place, "r", encoding='utf-8') as tmpjson:
      return json.load(tmpjson)
  except:
    with open(backup_place, "r", encoding='utf-8') as tmpjson:
      return json.load(tmpjson)

def save_json(tmp, place, backup_place = None):
  try:
    if tmp:
      with open(place, 'w', encoding='utf-8') as tmpjson:
        try:
          json.dump(tmp, tmpjson, ensure_ascii=False, sort_keys=True, indent = 4,  default = support_datetime_default)
          return True
        except Exception as e:
          print(e)
          return False
    else:
      return True
  except Exception as e:
    print(e)
    return False

def copy_json(place, backup_place = None):
    shutil.copy2(place, backup_place)
def get_jpn_time():
    return  datetime.utcnow()+timedelta(hours = 9)
class Ping(object):
    def __init__(self, host):
        loss_pat='0 received'
        msg_pat='icmp_seq=1 '
        ping = subprocess.Popen(
            ["ping", "-c", "1", host],
            stdout = subprocess.PIPE,
            stderr = subprocess.PIPE,
            shell = False,
            close_fds = True
        )
        out, error = ping.communicate()
        msg = ''
        if error:
          p(error)
          self.is_connectable = False
        else:
          for bline in out.splitlines():
              line = str(bline)[2:-1]
              if line.find(msg_pat)>-1:
                  msg = line.split(msg_pat)[1] # エラーメッセージの抽出
              if line.find(loss_pat)>-1: # パケット未到着ログの抽出
                  flag=False
                  break
          else:
              flag = True # breakしなかった場合 = パケットは到着している
          if flag:
              print('[OK]: ' + 'ServerName->' + host)
              self.is_connectable = True
          else:
              print('[NG]: ' + 'ServerName->' + host + ', Msg->\'' + msg + '\'')
              self.is_connectable = False
def reconnect_wifi():
    try:
        networksetup_cmd = '/usr/sbin/networksetup'
        optionargs = ['off']
        args = [networksetup_cmd, '-setairportpower', 'en0']
        i = 0
        while True:
          p(i)
          i += 1
          subprocess.Popen(
              args + ['off'],
              stdin = subprocess.PIPE,
              stdout = subprocess.PIPE,
              stderr = subprocess.PIPE,
              shell = False,
              close_fds = True
          )
          p('wifi network has been turned off... and restarting')
          p('wait 2sec...')
          time.sleep(1)
          p('wait 1sec...')
          time.sleep(1)
          subprocess.Popen(
              args + ['on'],
              stdin = subprocess.PIPE,
              stdout = subprocess.PIPE,
              stderr = subprocess.PIPE,
              shell = False,
              close_fds = True
          )
          if i > 3:
            return False
          p('reconnecting wifi, wait 6sec...')
          time.sleep(4)
          p('checking ping...')
          time.sleep(2)
          if Ping('google.com').is_connectable:
            p('ping is connecting. reconnect-program -> finished!!!!')
            break
          else:
            p('ping is NOT connecting... restart -> reconnect-program...')
            time.sleep(2)
        p('reconnected_wifi: ', get_jpn_time())
        return True
    except:
        return False
def t2t(strtime):
    return datetime.strptime(strtime, '%Y-%m-%dT%H:%M:%S.%f')


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def compact(tglist):
    return [ele for ele in tglist if ele]

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]

def getDeepPathDic(DIR):
  def _filebool(jpg):
    if jpg in {'.DS_Store'}:
      return False
    elif '.' in jpg:
      return True
    else:
      return False
  clsdirs = os.listdir(DIR)
  clsdirs = [clsdir for clsdir in clsdirs if not clsdir in {'.DS_Store'}]
  imgdics = list(chain.from_iterable([[(''.join([clsdirs[i],'/', jpg]), i)  for jpg in os.listdir(DIR + clsdirs[i]) if _filebool(jpg)] for i in range(len(clsdirs))]))
  return imgdics

def crowlDic(text = 'test', dic = {}):
  def _func(A):
    if A in text:
      return dic[A]
  anss =  [react for react in [_func(atg) for atg in dic] if react != None]
  if anss != []:
    return anss[0]
  else:
    return ''
# ['a', 's', 'c']
def crowlList(text = 'test', dic = ['']):
  anss =  [tg for tg in set(dic) if tg in text]
  # print(anss)
  if anss:
    return anss[0]
  else:
    return ''

def clean_text(text, isKaigyouOFF = False):
  text = re.sub(r'(@[^\s　]+)', '', text)
  text = re.sub(r'(#[^\s　]+)', '', text)
  # text = re.sub(r'(http[^\s　]+)', '', text)
  text = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', text)
  text = re.sub(r'(^[\s　]+)', '', text)
  text = re.sub(r'([\s　]+$)', '', text)
  text = text.replace('&lt;', '<').replace('&gt;', '>')
  if isKaigyouOFF:
    text = re.sub(r'(([\s　]+))', '', text)
  return text

def clean_text2(text):
   text = re.sub(r'[!-/:-@[-`{-~]', '', text)
   text = re.sub(r'(([\s　]+))', '', text)
   text = text.replace('w', '').replace('.', '').replace('…', '')
   return text

def sigmoid(z):
  return 1/(1+np.exp(-z)) if -100. < z else 0.

def adjustSize(DIR):
  clsdirs = os.listdir(DIR)
  clsdirs = [clsdir for clsdir in clsdirs if not clsdir in {'.DS_Store'}]
  dics = [(clsdir, os.listdir(DIR + clsdir)) for clsdir in clsdirs]
  lendic = [len(adds) for clsdir, adds in dics]
  maxsize = np.max(lendic)
  per = np.around(maxsize/lendic)
  [[[shutil.copy2(''.join([DIR, dics[i][0], '/', add]), ''.join([DIR, dics[i][0], '/copy', str(k), '_', add])) for add in dics[i][1] if not add in {'.DS_Store'}] for k in range(int(per[i])) if k != 0] for i in range(len(clsdirs))]

def sec2HMSstr(sec):
  hours = 0
  minutes = 0
  if sec>3600:
    hours = int(round(sec/3600,1))
    sec -= hours*3600
  if sec > 60:
    minutes = int(round(sec/60,1))
    sec -= minutes*60
  return ''.join([str(hours),'時間',str(minutes),'分', str(sec),'秒'])

def download_file(url, DIR, filename = ''):
  if not filename:
    filename = url.replace('/', '_')
  abs_filename = '/'.join([DIR, filename])
  if not os.path.exists(DIR):
    os.mkdir(DIR)
  print(abs_filename)
  try:
    urllib.request.urlretrieve(url, abs_filename)
    return abs_filename
  except IOError:
    print("[ERR.DL]")
    return ''

def saveMedias(status, ID, DIR):
  def saveMedia(medias, ID, i, screen_name):
    m = medias[i]
    media_url = m['media_url']
    if not ID is None:
      ID = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = ''.join([DIR,'/',ID,'_',str(i),'_',screen_name, '.jpg'])
    if not os.path.exists(DIR):
      os.mkdir(DIR)
    try:
      urllib.request.urlretrieve(media_url, filename)
      print(filename)
      return filename
    except IOError:
      print ("[ERR.SAVE.img]")
      return ''
  try:
    medias = status['extended_entities']['media']
    # print(status)
    return [filename for filename in [saveMedia(medias, ID, i, status['user']['screen_name']) for i in range(len(medias))] if filename != '']
  except Exception as e:
    print(e)

def saveImg(media_url, DIR, filename):
  if not os.path.exists(DIR):
    os.mkdir(DIR)
  try:
    absfilename = '/'.join([DIR,filename])
    if os.path.exists(absfilename):
      os.remove(absfilename)
    urllib.request.urlretrieve(media_url, absfilename)
    print(absfilename)
    return absfilename
  except IOError:
    print ("[ERR.SAVE.img]")
    return ''


def getRandIMG(DIR):
  pics = [fn for fn in os.listdir(DIR) if not fn == '.DS_Store']
  pic = np.random.choice(pics)
  return '/'.join([DIR, pic])

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
class a(MyObject):
  def __init__(self):
    self.b = 1
if __name__ == '__main__':
  # adjustSize(DIR)
  s = '@yohane_t  最近絵里が可愛いです……'
  # a = a()
  # a = BotProfile()
  # p(a)
  # p(s, 'aaa', s, is_print = True)
  # p(a.is_in('b'))
  # DIR = "/Users/masaMikam/Desktop/Data" + '/imgs/ガチャ'
  # print(getRandIMG(DIR))
  # reconnect_wifi()
  # print(crowlDic(text = 'ためし', dic = tmp["reactWord"]))
  # crowlList(text = s, dic = ['あ'])
  # print(clean_text2(s))

  # print(TEMP)
  # TEMP['test2'] = {'a':22}
  # print(TEMP)
  # saveTEMP(TEMP)
  # print(getRandIMG('/Users/masaMikam/OneDrive/imgs/learn/_work/海未'))
  # print(sec2HMSstr(50))
  # csv = '37,00,2016/02/16 14:34:00,9,3,ND20160216143311,2016/02/16 12:33:01,40.4,142.2,岩手県沖,50,3.6,2,1,0'
  # al = eew(csv, standard = 2)
  # print(al)


