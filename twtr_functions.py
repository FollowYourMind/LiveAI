#!/usr/bin/env python
# -*- coding:utf-8 -*-

#MY MODULEs
#variables
from setup import *
import _
from _ import p, d, MyObject, MyException
import natural_language_processing
import operate_sql
import main
class StreamListener(tweepy.streaming.StreamListener):
	def __init__(self, bot_id, lock):
		super().__init__()
		p(bot_id)
		self.bot_id = bot_id
		self.response_main = main.StreamResponseFunctions(bot_id, lock)
		self.response_main.on_initial_main()
		self.processes = []
	def __del__(self):
		p(self.bot_id, 'stopping streaming...')
		_.process_finish(self.processes)
	def on_connect(self):
		return True
	def on_friends(self, friends):
		return self.response_main.on_friends_main(friends)

	@_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	def on_status(self, status):
		# status_main_process = multiprocessing.Process(target = self.response_main.on_status_main, args=(status._json,), name=self.bot_id)
		# self.processes.append(status_main_process)
		# status_main_process.start()
		# return True
		return self.response_main.on_status_main(status._json)

	@_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
	def on_direct_message(self,status):
		# try:
		# 	dm_main_process = multiprocessing.Process(target = self.response_main.on_direct_message_main, args=(status._json,), name=self.bot_id)
		# 	dm_main_process.start()
		# 	return True
		return self.response_main.on_status_main(status._json)
		# except Exception as e:
		# 	d('StreamListener on_direct_message',e)
		# 	return True
		# return self.response_main.on_direct_message_main(status._json)
	def on_event(self, status):
		return self.response_main.on_event_main(status._json)
	def on_limit(self, track):
		p(track, 'track')
		return True
	def keep_alive(self):
		p('|')
		return True
	def on_exception(self, exception):
		p(exception, 'exception')
		return True
	def on_warning(self, notice):
		p(notice, 'warning')
		return True
	def on_disconnect(self, notice):
		d(notice, 'disconnect')
		return False
	def on_error(self,status):
		p('cannot get')
		return False
	def on_timeout(self):
		p('timeout...')
		return False
def get_twtr_auth(auth_dic):
	try:
		CONSUMER_KEY = auth_dic['consumer_key']
		CONSUMER_SECRET = auth_dic['consumer_secret']
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		ACCESS_TOKEN = auth_dic['access_token_key']
		ACCESS_SECRET = auth_dic['access_token_secret']
		auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
		return auth
	except:
		pass
class TwtrTools:
	def __init__(self, bot_id = 'LiveAIs', lock = None):
		self.bot_id = bot_id
		api_keys = cfg['twtr']
		twtr_auths = {key: get_twtr_auth(value) for key, value in api_keys.items()}
		twtr_apis = {key: tweepy.API(value, wait_on_rate_limit = True) for key, value in twtr_auths.items()}
		self.lock = lock
		self.twtr_auth = twtr_auths[bot_id]
		self.twtr_api = twtr_apis[bot_id]
	def Stream(self):
		auth = self.twtr_auth
		while True:
			try:
				stream = tweepy.Stream(auth = auth, listener = StreamListener(self.bot_id, self.lock), timeout = 60, async = True, secure=True)
				stream.userstream()
			except tweepy.TweepError as e:
				d(e, 'twf.stream tweeperror waiting 100sec')
				time.sleep(100)
			except Exception as e:
				d(e, 'twf.stream waiting 100sec')
				time.sleep(100)
				# stream = tweepy.Stream(auth = auth, listener = StreamListener(self.bot_id), async = True, secure=True)
	def get_status(self, status_id):
		try:
			return self.twtr_api.get_status(id = status_id)
		except tweepy.error.TweepError as e:
			return None
	def send(self, ans, screen_name = '', status_id = '', imgfile = '', mode = 'dm', try_cnt = 0):
		if mode == 'dm':
			return self.send_direct_message(ans = ans, screen_name = screen_name)
		elif mode == 'open':
			return self.send_tweet(ans = ans, screen_name = '', status_id = '', imgfile = imgfile, is_debug = is_debug, try_cnt = try_cnt)
		else:
			return self.send_tweet(ans = ans, screen_name = screen_name, status_id = status_id, imgfile = imgfile, is_debug = is_debug, try_cnt = try_cnt)
	def tweet(self, ans, screen_name = '', status_id = '', imgfile = '', is_debug = False,  try_cnt = 0):
		p('old')
		return self.send_tweet(self, ans, screen_name = '', status_id = '', imgfile = '', is_debug = False, try_cnt = 0)
	def send_tweet(self, ans, screen_name = '', status_id = '', imgfile = '', is_debug = False,  try_cnt = 0):
		try:
			if screen_name:
				ans1 = ''.join(['@', screen_name,' ', ans]).replace('@@', '@')
			else:
				ans1 = ans

			if len(ans) > 140:
				is_split = True
				ans2 = ''.join([ans1[0:139], '…'])
			else:
				is_split = False
				ans2 = ans1
			if imgfile:
				if not is_debug:
					tweetStatus = self.twtr_api.update_with_media(imgfile, status = ans2, in_reply_to_status_id = status_id)
					print('[Tweet.IMG.OK] @', screen_name, ' ', ans2)
				else:
					print('[Debug][Tweet.IMG.OK] @', screen_name, ' ', ans2)
			else:
				if not is_debug:
					tweetStatus = self.twtr_api.update_status(status = ans2, in_reply_to_status_id = status_id)
					print('[Tweet.OK] @', screen_name, ' ', ans2)
				else:
					print('[Debug][Tweet.OK] @', screen_name, ' ', ans2)
			# 140字越えの際は、分割ツイート
			if is_split:
				if screen_name:
					try_cnt += 1
					return self.tweet(''.join(['...', ans[139:]]), screen_name = screen_name, status_id = status_id, is_debug = is_debug, try_cnt = try_cnt)
				else:
					return True
			else:
				return True
		except tweepy.error.TweepError as e:
			print('[ERR][Tweet.TweepError] @', screen_name, ' ', ans)
			p(e)
			if e.response and e.response.status == 403:
				print('403')
				return False
			else:
				return True
		except Exception as e:
			print('[Tweet.ERR] @', screen_name, ' ', ans)
			print(e)
			return False

	def send_direct_message(self, ans, screen_name = '', is_debug = False, try_cnt = 0):
		try:
			if not is_debug:
				tweetStatus = self.twtr_api.send_direct_message(screen_name = screen_name, text = ans)
				print('[DM.OK] @', screen_name, ' ', ans)
			else:
				print('[Debug][DM.OK] @', screen_name, ' ', ans2)
			return True
		except tweepy.error.TweepError as e:
			print('[ERR][DM.TweepError] @', screen_name, ' ', ans)
			if e.response and e.response.status == 403:
				print('403')
				return False
			else:
				return True
		except Exception as e:
			print('[DM.ERR] @', screen_name, ' ', ans)
			print(e)
			return False

	# def send_direct_message(self, ans, screen_name = '', tmp = {'tweetStatus': {'is_debug':False, 'isSplitTweet': False, 'tempStop_since':0}}):
	# 	try:
	# 		if not tmp['tweetStatus']['is_debug']:
	# 			tweetStatus = self.twtr_api.send_direct_message(screen_name = screen_name, text = ans)
	# 			print('[DM.OK] @', screen_name, ' ', ans)
	# 		else:
	# 			print('[Debug][DM.OK] @', screen_name, ' ', ans2)
	# 		return True, tmp
	# 	except tweepy.error.TweepError as e:
	# 		print('[ERR][DM.TweepError] @', screen_name, ' ', ans)
	# 		if e.response and e.response.status == 403:
	# 			print('403')
	# 			tmp['tweetStatus']['tempStop_since'] = tmp['now']
	# 			return False, tmp
	# 		else:
	# 			return True, tmp
	# 	except Exception as e:
	# 		print('[DM.ERR] @', screen_name, ' ', ans)
	# 		print(e)
	# 		return False, tmp

	def getTrendwords(self, mode = 'withoutTag'):
		# 'locations': [{'woeid': 23424856, 'name': 'Japan'}]
		trends = self.twtr_api.trends_place(id = 23424856)[0]['trends']
		if mode == 'withoutTag':
			return [trend['name'] for trend in trends if not '#' in trend['name']]
		elif mode == 'withTag':
			trendtags = [trend['name'] for trend in trends if '#' in trend['name']]
			trendwords = [trend['name'] for trend in trends if not '#' in trend['name']]
			return trendwords, trendtags
		else:
			return [trend['name'] for trend in trends]
	def update_profile(self, name, description, location, url = '', filename = '', BGfilename = '', Bannerfilename = ''):
		try:
			self.twtr_api.update_profile(name = name, url = url,  location = location, description = description)
			if filename:
				self.twtr_api.update_profile_image(filename)
			if BGfilename:
				self.twtr_api.update_profile_background_image(BGfilename)
			if Bannerfilename:
				self.twtr_api.update_profile_banner(Bannerfilename)
			return True
		except Exception as e:
			print(e)
			return False
	def is_create_list_success(self, name, mode = 'private', description = ''):
		try:
			self.twtr_api.create_list(name = name, mode = mode, description = description)
			return True
		except:
			return False
	def get_listmembers_all(self, username, listname):
		try:
			return [UserObject.screen_name for UserObject in tweepy.Cursor(self.twtr_api.list_members, username, listname).items()]
		except tweepy.error.TweepError as e:
			if e.api_code == '34':
				if username == self.bot_id:
					p(listname, 'MAKE the LIST!!')
			# 		self.is_create_list_success(name = listname)
			return []
		except:
			return []
	def get_followers_all(self, screen_name):
		return self.twtr_api.followers(screen_name = screen_name)
	def give_fav(self, status_id):
		try:
			self.twtr_api.create_favorite(id = status_id)
		except :
			return False
		else:
			return True
	def get_userinfo(self, screen_name):
		try:
			return self.twtr_api.get_user(screen_name = screen_name)._json
		except :
			pass
	def is_destroy_friendship_success(self, screen_name):
		try:
			self.twtr_api.destroy_friendship(screen_name = screen_name)
			return True
		except:
			return False
	def is_create_friendship_success(self, screen_name):
		try:
			self.twtr_api.create_friendship(screen_name = screen_name)
			return True
		except:
			return False
	def convert_direct_message_to_tweet_status(self, status):
  		s = status['direct_message']
  		s['user'] = {}
  		s['user']['screen_name'] = s['sender_screen_name']
  		s['user']['name'] = s['sender']['name']
  		s['user']['id_str'] = s['sender']['id_str']
  		s['in_reply_to_status_id_str'] = None
  		s['in_reply_to_screen_name'] = self.bot_id
  		s['extended_entities'] = s['entities']
  		s['retweeted'] = False
  		s['is_quote_status'] = False
  		return s
	def download_userobject_urls(self, userobject, DIR = DIRusers):
		screen_name = userobject.screen_name
		USERDIR = '/'.join([DIR, screen_name])
		if not os.path.exists(USERDIR):
			os.mkdir(USERDIR)
		try:
			userobject.abs_icon_filename = _.saveImg(media_url = userobject.profile_image_url.replace('_normal', ''), DIR = USERDIR, filename = ''.join([screen_name, '_icon.jpg']))
		except Exception as e:
			print('[ERR]imitate.icon')
			print(e)
			userobject.abs_icon_filename = ''
		try:
			userobject.abs_background_filename = _.saveImg(media_url = userobject.profile_background_image_url, DIR = USERDIR, filename = ''.join([screen_name, '_background.jpg']))
		except Exception as e:
			print('[ERR]imitate.bg')
			print(e)
			userobject.abs_background_filename = ''
		try:
			userobject.abs_banner_filename = _.saveImg(media_url = userobject.profile_banner_url, DIR = USERDIR, filename = ''.join([screen_name, '_banner.jpg']))
		except Exception as e:
			print('[ERR]imitate.banner')
			print(e)
			userobject.abs_banner_filename = ''
		return userobject
	def imitate(self, screen_name, DIR = DIRusers):
		try:
			user = self.twtr_api.get_user(screen_name = screen_name)
			user = self.download_userobject_urls(user, DIR = DIR)
			alt_name = user.name.replace(' ', '')
			alt_description = user.description
			is_following = user.following
			if not is_following:
				return False

			self.update_profile(name = alt_name, description = alt_description, location = ''.join(['まねっこ中@', screen_name]), url = '', filename = user.abs_icon_filename, BGfilename = user.abs_background_filename, Bannerfilename = user.abs_banner_filename)
			return True
		except Exception as e:
			print('[ERR]imitate')
			print(e)
			return False

if __name__ == '__main__':
	twf = TwtrTools('LiveAI_Alpaca')
	objs = twf.get_followers_all('LiveAI_Maki')
	p(objs[0]._json)
	# twf.Stream()
	# ans = twf.get_listmembers_all(username = 'LiveAI_Rin' , listname = 'BOaaa')
	# ans = twf.get_status(status_id = '715662952372699136')
	# p(ans._json['user']['screen_name'])
	# twf.imitate(screen_name = 'LiveAI_Umi', DIR = DIRusers)
	# twf.send(ans = 'testです', screen_name = '_mmkm', status_id = '', imgfile = '', mode = 'dm',  trycnt = 0)









