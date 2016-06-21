#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import _
from _ import p, d, MyObject, MyException
import urllib
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import bs4
# MY PROGRAMs

def get_bs4soup_old(url):
	header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	html = urllib.request.urlopen(url)
	soup = bs4.BeautifulSoup(html, 'lxml')
	return soup
def get_bs4soup(url):
	USER_AGENT = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error
	# Selenium settings
	phantomjs_path = '/usr/local/bin/phantomjs'
	# phantomjs_args = [ '--proxy=proxy.server.no.basho:0000', '--cookie-file={}'.format("cookie.txt") ] service_args=phantomjs_args
	driver = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull, desired_capabilities={'phantomjs.page.settings.userAgent':USER_AGENT})
	# get a HTML response
	driver.get(url)
	html = driver.page_source.encode('utf-8')  # more sophisticated methods may be available
	soup = bs4.BeautifulSoup(html, 'lxml')
	# ss = driver.execute_script('return loadDisqus();')
	# p(ss)
	return soup
def extract_ss(url = 'http://www.lovelive-ss.com/?p={}'):
	soup = get_bs4soup(url)
	title = soup.find('h1', class_="entry-title")
	if title is None:
		return None
	else:
		p(title.get_text(), url)
	try:
		ss_contents = soup.find("div", class_ = "entry-content").find_all("dd", class_ ="t_b")
	except:
		return None
	def op_soup(content):
		a_conts = content.find_all('a')
		[a_cont.extract() for a_cont in a_conts if not a_cont is None]
		return content.get_text()
	s_ls = [op_soup(ss_content) for ss_content in ss_contents]
	return s_ls
def search_weblioEJJE(word = 'ask'):
	try:
		converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
		ejje_url = ''.join(["http://ejje.weblio.jp/content/", converted_word])
		soup = get_bs4soup(ejje_url)
		return ''.join(['\'', word, '\'の訳:\n', str(soup.find("div", class_ = "summaryM")).split('</b>')[1][:-6]])
	except Exception as e:
		d(e)
		return ''.join(['\'', word, '\'に一致する語は見つかりませんでした。'])

def search_wiki(word = 'クロマニョン人'):
	ans = ''
	try:
		converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
		wiki_url = ''.join(["https://ja.wikipedia.org/wiki/", converted_word])
		soup = get_bs4soup(wiki_url)
		ptext = soup.findAll("p")
		pstr =  ''.join([p.get_text() for p in ptext])
		ans = re.sub(re.compile('\<.+\>'), '' , pstr)
		ans = ans.replace('この記事には複数の問題があります。改善やノートページでの議論にご協力ください。', '').replace('■カテゴリ / ■テンプレート', '')
		anslist = [re.sub(re.compile('\[.+\]'), '' , s) for s in ans.split('。')]
		ans = ''.join(['。'.join(anslist[:8]), '。']).replace('。。', '。')
		return ans
	except Exception as e:
		d(e)
		return ''.join(['\'', word, '\'に一致する語は見つかりませんでした。'])

def get_dl_links(url = "https://www.jstage.jst.go.jp/browse/jspa1962/-char/ja/", extention = 'pdf', except_str = 'pub', DIR = DATADIR, sleep_time = 1):
	abs_filename_ls = []
	try:
		soup = get_bs4soup(url)
		links = soup.findAll('a')
		download_urls = [href for href in [link.get('href') for link in links] if href and extention in href and not except_str in href]
		BASE_URL = '/'.join(url.split('/')[:3])
		downloads_cnt = len(download_urls)
		error_cnt = 0
		p(''.join([str(downloads_cnt), '件のファイルをダウンロードします。']))
		for i in range(downloads_cnt):
			time.sleep(sleep_time)
			try:
				target_url = ''.join([BASE_URL, download_urls[i]])
				p(target_url)
				filename = '.'.join([target_url.split('/')[-2], extention])
				abs_filename_ls.append(_.download_file(url = target_url, DIR = DIR, filename = filename))
			except:
				error_cnt += 1
				pass
			p(''.join(['COMPLETE:', str(i-error_cnt+1), '/', str(downloads_cnt), '\tERR:', str(error_cnt)]))
		return abs_filename_ls
	except Exception as e:
		p(e)
		return abs_filename_ls
def get_ss(word = 'クロマニョン人'):
	ans = ''
	try:
		converted_word = urllib.parse.quote_plus(word, encoding="utf-8")
		wiki_url = ''.join(["https://ja.wikipedia.org/wiki/", converted_word])
		soup = get_bs4soup(wiki_url)
		ptext = soup.findAll("p")
		pstr =  ''.join([p.get_text() for p in ptext])
		ans = re.sub(re.compile('\<.+\>'), '' , pstr)
		ans = ans.replace('この記事には複数の問題があります。改善やノートページでの議論にご協力ください。', '').replace('■カテゴリ / ■テンプレート', '')
		anslist = [re.sub(re.compile('\[.+\]'), '' , s) for s in ans.split('。')]
		ans = ''.join(['。'.join(anslist[:8]), '。']).replace('。。', '。')
		return ans
	except Exception as e:
		d(e)
		return ''.join(['\'', word, '\'に一致する語は見つかりませんでした。'])
if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		text = argvs[1]
		user = argvs[2]
	except:
		user = 'p_eval'
		text = "皇居"
	url = 'http://www.lovelive-ss.com/?p=8560'
	# soup = get_bs4soup(url)
	# p(soup)
	import operate_sql
	import natural_language_processing
	site_url = 'http://www.lovelive-ss.com/?p={}'
	# range(4538, 8000):
	# reg = natural_language_processing.RegexTools()
	# for ss_number in range(4557, 8000):
	# 	p(ss_number)
	# 	try:
	# 		url = site_url.format(ss_number)
	# 		ss_ls = extract_ss(url = url)
	# 		if ss_ls:
	# 			operate_sql.save_ss(url = url, texts = ss_ls, retry_cnt = 0)
	# 		# datas = operate_sql.get_ss(url = url)
	# 		# text = ''.join([data.text for data in datas])
	# 		# p(reg.extract_discorse(text))
	# 		# operate_sql.save_ss_dialog(url)
	# 	except Exception as e:
			# d(e)
		# time.sleep(1+np.random.rand()*3)
	# p(1+np.random.rand()*3)
	operate_sql.save_ss(url = url, texts = ['a', 'ss'])
	# extract_ss(url = 'http://www.lovelive-ss.com/?p=22')
	# p(os.environ['PATH'])
	# print(search_wiki(word = '官僚制'))
	# get_dl_links('http://www.fsa.go.jp/news/newsj/16/ginkou/f-20050629-3.html', extention = 'pdf', DIR = '/Users/masaMikam/Dropbox/Research/金融庁分析', sleep_time = 1)
# 	while len(ans) > 130:
# 		ans = '。'.join(ans.split('。')[:-2])
# 	ans = ''.join([ans, '。'])
# 	print(ans)
# 	print(len(ans))
	# s = 'GIRLS und PANZER[注釈 1]は、'
	# face_char = re.compile('\[.+\]')
	# facelist = face_char.findall(s)
	# cleaned = re.sub(re.compile('\[.+\]'), '' , s)
	# print(cleaned)
	# cmdlist = text.split(' ')
	# text = cmdlist[0]
	# ret = SRTR(text, user)
	# print(ret)