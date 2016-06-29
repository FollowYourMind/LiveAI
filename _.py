#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from setup import *
import os
import sys
import traceback
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
import queue
from datetime import datetime, timedelta
from collections import Counter, deque
from itertools import chain

import functools
from functools import partial
from contextlib import contextmanager
try:
    from decorator import decorator
except ImportError:
    def decorator(caller):
        """ Turns caller into a decorator.
        Unlike decorator module, function signature is not preserved.
        :param caller: caller(f, *args, **kwargs)
        """
        def decor(f):
            @functools.wraps(f)
            def wrapper(*args, **kwargs):
                return caller(f, *args, **kwargs)
            return wrapper
        return decor

class SetQueue(queue.Queue):
    def _init(self, maxsize):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()

def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        stime = time.clock()
        ret = func(*args, **kw)
        etime = time.clock()
        print('{0}: {1:,f}ms'.format(func.__name__, (etime-stime)*1000))
        return ret
    return wrapper

def forever(exceptions = Exception, is_print = True, is_logging = True, ret = True):
    def _forever(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                wret = func(*args, **kw)
            except exceptions:
                log_err(is_print, is_logging)
                wret = ret
            return wret
        return wrapper
    return _forever

@contextmanager
def forever_with(exceptions = Exception, is_print = True, is_logging = True):
    is_bug = False
    try:
        yield is_bug
    except exceptions:
        log_err(is_print, is_logging)
        is_bug = True


def deco_tag(tag):
    def _deco_tag(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            res = '<'+tag+'>'
            res = res + func(*args,**kwargs)
            res = res + '</'+tag+'>'
            return res
        return wrapper
    return _deco_tag
def deco_sql(db):
    def _deco_sql(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            try:
                with db.transaction():
                    res = func(*args,**kwargs)
            except IntegrityError as e:
                db.rollback()
                raise
            except Exception as e:
                err_msg,  traceback_ls = _.log_err(is_print = True, is_logging = True)
            else:
                return res
        return wrapper
    return _deco_sql
#logging
from logging import basicConfig, getLogger,StreamHandler,DEBUG
import logging.config
logging.config.fileConfig('log_config.ini')
logger = getLogger(__name__)
# basicConfig(filename='log.txt')
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
def log_err(is_print = True, is_logging = True):
      # エラーの情報をsysモジュールから取得
    info = sys.exc_info()
    if info[0] is None:
      return
    # tracebackモジュールのformat_tbメソッドで特定の書式に変換
    tbinfo = traceback.format_tb(info[2])
    # 収集した情報を読みやすいように整形して出力する----------------------------
    err_info = ''.join(['\n'.join(tbinfo), str(info[1])])
    err = '\n'.join(['PythonError.'.ljust( 80, '=' ), err_info, '\n'.rjust( 80, '=' )])
    if is_print:
      print(err)
    if is_logging:
      logger.debug(err_info)
    return info[1], tbinfo

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

def __retry_internal(f, exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0,
                     logger=logger):
    """
    Executes a function and retries it if it failed.
    :param f: the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    _tries, _delay = tries, delay
    while _tries:
        try:
            return f()
        except exceptions as e:
            _tries -= 1
            if not _tries:
                raise

            if logger is not None:
                logger.warning('%s, retrying in %s seconds...', e, _delay)

            time.sleep(_delay)
            _delay *= backoff

            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter

            if max_delay is not None:
                _delay = min(_delay, max_delay)

def retry(exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1, jitter=0, logger=logger):
    """Returns a retry decorator.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logger. if None, logging is disabled.
    :returns: a retry decorator.
    """
    @decorator
    def retry_decorator(f, *fargs, **fkwargs):
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return __retry_internal(partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff, jitter,
                                logger)
    return retry_decorator
def retry_call(f, fargs=None, fkwargs=None, exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1,
               jitter=0,
               logger=logger):
    """
    Calls a function and re-executes it if it failed.
    :param f: the function to execute.
    :param fargs: the positional arguments of the function to execute.
    :param fkwargs: the named arguments of the function to execute.
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logger. if None, logging is disabled.
    :returns: the result of the f function.
    """
    args = fargs if fargs else list()
    kwargs = fkwargs if fkwargs else dict()
    return __retry_internal(partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff, jitter, logger)

@contextmanager
def process_with(auto_start = True):
    processes = []
    try:
        yield processes
        if auto_start:
            [process.start() for process in processes if not process.is_alive()]
    finally:
        process_finish(processes)

def process_finish(processes):
    try:
        for process in processes:
            if process.is_alive():
                process.join()
    except KeyboardInterrupt:
        for worker in processes:
            if worker.is_alive():
                worker.terminate()
                worker.join()

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
def restart_program():
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    python = sys.executable
    os.execl(python, python, * sys.argv)

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
        if Ping('google.com').is_connectable:
            p('ping is connecting. reconnect-program -> finished!!!!')
            return True
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
          time.sleep(5)
          p('checking ping...')
          time.sleep(5)
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
def convert_gram(ls, n_gram = 3):
    len_ls = len(ls)
    max_i = len_ls - n_gram +1
    ans =  [[ls[i+k] for k in range(n_gram)] for i in range(len_ls) if -1 < i < max_i]
    return ans

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

def queue_put(q, msg, timeout = 5):
    import queue
    try:
        q.put(msg, timeout)
    except queue.Full:
       d('tweet_log_sender put() timed out. Queue is Full')
       raise
if __name__ == '__main__':
  # adjustSize(DIR)
  sq = SetQueue()
  sq.put(('a', 3))
  a = sq.get()
  p(a)
  sq.put('a')    
  sq.put('b')
  sq.put('b')
  sq.put('c')
  while True:
    a = sq.get()
    p(a)
  # reconnect_wifi()
  # import sys, traceback
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


