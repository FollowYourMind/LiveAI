#!/usr/bin/env python
# -*- coding:utf-8 -*-

#MY MODULEs
#variables
import asyncio
from setup import *
from sql_models import *
import natural_language_processing
import _
from _ import p, d, MyObject, MyException
import machine_learning_img
import dialog_generator
import twtr_functions
import opencv_functions
import crawling
import game_functions
import operate_sql
import queue
import random
# def get_kusoripu(tg1, is_open = False):
#     ans = operate_sql.get_kusoripu(n = 3000)
#     if '{ID}' in ans:
#         ans = ans.format(ID= ''.join(['@', tg1, ' ']))
#     else:
#         ans = ''.join(['@', tg1,' \n', ans])
#     if '{name}' in ans:
#         ans = ans.format(name= 'アルパカ')
#     return ans
def is_kusoripu(s):
    if len(s) < 100:
        return False
    if 'http' in s:
        return False
    if '#' in s:
        return False
    # if s.count('\n') > 6:
    #     return True
    if s.count('\u3000') > 5:
        return True
    if s.count('\t') < 5:
        return False
    emoji_cnt = len(re.findall('[\U0001F0CF-\U000207BF]', s))
    if emoji_cnt > 5:
        return True
    kigou_cnt = len(re.findall('[!-/:-@[-`{-~]', s))
    if kigou_cnt < 5:
        return False
    if kigou_cnt > 20:
        return True
    hankaku_katakana_cnt = len(re.findall('[ｦ-ﾟ]', s))
    if hankaku_katakana_cnt > 7:
        return True
    return False

def is_kusa(s):
    if s.count('w') >15:
        return True
    return False
def extract_cmds_dic(text):
    try:
        reg = '\s*(\w+)\s*([!-/:-@≠\[-`{-~]*)\s*[@#]*(\w+)'
        p = re.compile(reg, re.M)
        reg_ls = p.findall(text)
        text = re.sub(p, '', text)
        #-- と空白で挟まれたものをコマンドにする
        return {reg[1]: reg[3] for reg in reg_ls}, text
    except:
        return {}, text

def mod_intimacy(intimacy, is_increase = True):
    float_intimacy = float(intimacy)
    if is_increase:
        intimacy = float_intimacy + np.log2(120 - float_intimacy) /50
    else:
        intimacy = float_intimacy / 1.005
    return intimacy 


class Temp(MyObject):
    pass
class Stats(MyObject):
    def __init__(self):
        self.tweet_30min_cnt = 0
        self.reply_30min_cnt = 0
        self.tweet_30min_cnt = 0
        self.timeline_30min_cnt = 0
        self.direct_message_30min_cnt = 0
        self.faved_30min_cnt = 0
        self.fav_30min_cnt = 0
class TweetLogPool(MyObject):
    def __init__(self):
        self.my_twlog = []
        self.timeline_twlog = []
        self.directmessage_twlog = []
        self.status_ids = []
    def append_and_adjust_timeline_twlog(self, appendage_status):
        status_id = appendage_status['id_str']
        if not status_id in self.status_ids:
            self.timeline_twlog.append(appendage_status['clean_text'])
            self.status_ids.append(status_id)
            self.timeline_twlog = self.timeline_twlog[-20:]
class StreamResponseFunctions(MyObject):
    def __init__(self, bot_id, lock):
        self.bot_chara_dic = {
            'LiveAI_Umi': '海未',
            'LiveAI_Honoka': '穂乃果',
            'LiveAI_Kotori': 'ことり',
            'LiveAI_Rin': '凛',
            'LiveAI_Eli': '絵里',
            'LiveAI_Maki': '真姫',
            'LiveAI_Hanayo': '花陽',
            'LiveAI_Nozomi': '希',
            'LiveAI_Nico': 'にこ',
            'LiveAI_Yukiho':'雪穂',
            'LiveAI_Alisa': '亜里沙',
            'LiveAI_Alpaca': 'sys',
            'LiveAI_Chika': '千歌',
            'LiveAI_Yoshiko': '善子',
            'LiveAI_You': '曜',
            'LiveAI_Riko': '梨子',
            'LiveAI_Mari': '鞠莉',
            'LiveAI_Ruby': 'ルビィ',
            'LiveAI_Dia': 'ダイヤ',
            'LiveAI_Kanan': '果南',
            'LiveAI_Hanamaru': '花丸',
        }
        if not bot_id in self.bot_chara_dic:
            self.default_character = 'sys'
        else:
            self.default_character = self.bot_chara_dic[bot_id]
        self.bot_id = bot_id
        self.lock = lock
        self.atmarked_bot_id = ''.join(['@', self.bot_id])
        self.manager_id = 'kaihatsu_paka'
        self.twf = twtr_functions.TwtrTools(self.bot_id)
        #CLASS
        self.bot_profile = operate_sql.BotProfile(self.bot_id)
        self.tmp = Temp()
        self.stats = Stats()
        self.status_ids = []
        # 確率
        self.rate_active_talk = 0.01
        # デバッグ方式。
        debug_style = ''
        self.is_debug_direct_message = 'dm' in debug_style or 'all' in debug_style
        self.is_debug_tweet = 'tweet' in debug_style or 'all' in debug_style
        self.is_debug_event = 'event' in debug_style or 'all' in debug_style
        self.on_initial_main()

    def send(self, ans, screen_name = '', imgfile = '', status_id = '', mode = 'dm', try_cnt = 0):
        sent_status = None
        if self.stats.tweet_30min_cnt is None:
            self.stats.tweet_30min_cnt = 0
        # 30分あたりのツイート数が50を上回る場合、ツイートしない。
        if self.stats.tweet_30min_cnt > 50:
            duration = try_cnt + 1
            set_time = datetime.now(JST) + timedelta(hours=0, minutes = duration)
            operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': 'tweet', 'to_whom':screen_name, 'when':set_time, 'tmptext': ans, 'tmpid': status_id, 'tmpfile': imgfile, 'tmpcnt': try_cnt +1})
            p('[Tweet.1minAfter] @', screen_name, ' ', ans)
            return None
        else:
            # tweeet 数をインクリメントする
            self.stats.tweet_30min_cnt += 1
        if mode == 'dm':
            sent_status = self.twf.send_direct_message(ans, screen_name = screen_name, try_cnt = try_cnt)
        elif mode in {'open', 'tweet'}:
            sent_status = self.twf.send_tweet(ans, screen_name = screen_name, imgfile = imgfile, status_id = status_id, try_cnt = try_cnt)
        # if sent_status:
            # try:
            #     TweetStatus.create(_id = sent_status['id_str'], data = sent_status)
            # except:
            #     pass
            # finally:
        return sent_status
        # return None
    def default_profile(self):
        try:
            p(self.bot_profile)
            if not self.bot_profile.location is None:
                if 'imitating' in self.bot_profile.location:
                    self.bot_profile.location = '...'
            self.twf.update_profile(name = self.bot_profile.name, description = self.bot_profile.description, location= self.bot_profile.location, url = self.bot_profile.url, filename = self.bot_profile.abs_icon_filename, BGfilename = '', Bannerfilename = self.bot_profile.abs_banner_filename)
            return True
        except Exception as e:
            _.log_err()
            return False
    def on_initial_main(self):
        # self.bot_profile = Temp()
        p(self.bot_id+' >> Loading Initial_datas...')
        self.tmp.imitating = self.bot_id
        self.tmp.manager_id = self.manager_id
        self.tmp.bots_list = self.twf.get_listmembers_all(username = self.bot_id, listname = 'BOT')
        self.tmp.response_exception = self.twf.get_listmembers_all(username = self.bot_id, listname = 'responseException')
        self.bots_set = set(self.tmp.bots_list)
        self.response_exception_set = set(self.tmp.response_exception)
        self.tmp.trendwords_ls = self.twf.getTrendwords()
        self.eew_ids_set = {0}
        self.tmp.friend_ids = {}
        self.tmp.response = ['おはよう', 'おやすみ', 'ぬるぽ']
        p(self.bot_id+' >>Loaded setupDatas! => Loading FriendsIDs...')
    def on_friends_main(self, friends):
        self.tmp.friend_ids = friends
        self.friend_ids_set = set(friends)
        p(self.bot_id+' >>Loaded'+str(len(friends))+'FriendsIDs! => starting Streaming...')
    def check_tmpdatas(self):
        return True
    def construct_func(self, cmds_dic, function = 'add', baseparam_ls = [], param = 'label'):
        const = ''
        if param in cmds_dic[function]:
            const = cmds_dic[function][param]
        else:
            if param in baseparam_ls:
                key_index = baseparam_ls.index(param)
                key = '<key{}>'.format(str(key_index))
                if key in cmds_dic[function]:
                    const = cmds_dic[function][key]
        return const
    def response_eew(self, csv, standard = 0):
        eew = csv.split(',')
        eew_dic = {}
        if 'eew' in csv:
            eew_dic['title'] = '【(｡╹ω╹｡)実験中(｡╹ω╹｡)'
        elif eew[1] != '01':
            eew_dic['title'] = '【緊急地震速報'
        else:
            eew_dic['title'] = '[訓練]【緊急地震速報'
        eew_dic['date'] = eew[2]
        if eew[5] in self.eew_ids_set:
            if eew[3] in {'8', '9'}:
                eew_dic['title'] = ''.join(['[最終]', eew_dic['title']])
                self.eew_ids_set.remove(eew[5])
            else:
                return ''
        else:
            self.eew_ids_set.add(eew[5])
        eew_dic['time'] = eew[6].split(' ')[1]
        eew_dic['area'] = eew[9]
        eew_dic['depth'] = ''.join([eew[10], 'km'])
        eew_dic['magnitude'] = eew[11]
        eew_dic['seismic_intensity'] = eew[12]
        if eew[13] == '1':
            eew_dic['eqType'] = '海洋'
        else:
            eew_dic['eqType'] = '内陸'
        eew_dic['alert'] = eew[14]
        eew_alert = ''
        if eew[0] != '35':
            eew_alert = ''.join([eew_dic['title'], '<震度', eew_dic['seismic_intensity'], '> M', eew_dic['magnitude'], '】\n震源:', eew_dic['area'], ' (', eew_dic['eqType'], ')\n', eew_dic['time'], '発生', ' 深さ', eew_dic['depth']])
        else:
            eew_alert = ''.join([eew_dic['title'], '<震度', eew_dic['seismic_intensity'], '>】\n震源:', eew_dic['area'], ' (', eew_dic['eqType'], ')\n', eew_dic['time'], '発生', '深さ', eew_dic['depth']])
        return eew_alert

    @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = 50)
    def get_deltasec(self, time_future, time_past):
    #time_future - time_past時間計測(秒)
        try:
            delta = time_future - time_past
        except: #文字列対策
            logger.debug('convert str into datetime')
            delta = time_future - datetime.strptime(time_past, '%Y-%m-%d %H:%M:%S.%f')
        deltasec = delta.total_seconds()
        return deltasec
    def _convert_first_personal_pronoun(self, word, convert_word):
        if word in {'私', 'わたし', 'ぼく', '僕', 'あたし', 'おれ', '俺', 'オレ', '拙者', 'わし'}:
            return convert_word
        else:
            return word
    #MAIN FUNCTION
    @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
    def main(self, status, mode = 'dm', userinfo = '', userbot = ''):
        ans = ''
        ans_ls = []
        image_file = ''
        tweet_status = ''
        filename = ''
        text = status['clean_text']
        status_id = status['id_str']
        screen_name = status['user']['screen_name']
        nickname = ''.join([userinfo.nickname, 'さん'])
        bot_id = self.bot_id
        is_new_user_forchara = userbot.is_created
        is_new_user_forsystem = userinfo.is_created
        is_reply = self.bot_id in status['text']

        # userbot.context = text
        call_chara_ls = iscalledBOT(text = text,  select_set = {self.default_character})
        if not call_chara_ls:
            pass
        elif mode != 'dm' and not is_reply:
            return True
        elif any([call_phrase in text for call_phrase in {'おいで', 'かもん', 'hey', 'きて', 'こい', '来', '114514'}]):
            new_chara = call_chara_ls[0]
            if new_chara != userinfo.talk_with:
                ans = ''.join([userinfo.talk_with,'→', new_chara, '「', operate_sql.get_phrase(status = 'よびだし', character = new_chara), '」'])
                userinfo.talk_with = new_chara
            else:
                ans = ''.join([userinfo.talk_with,'「', operate_sql.get_phrase(status = 'よびだし', character = userinfo.talk_with), '」'])
            try:
                filename = _.getRandIMG(DATADIR + '/imgs/' + new_chara)
            except:
                filename = ''

        character = self.default_character
        text_without_tag = re.sub(r'(#[^\s　]+)', '', status['text'])
        text_without_tag_url = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', text_without_tag)
        text_without_tag_url_ownid = text_without_tag_url.replace(self.atmarked_bot_id, '')
        dialog_obj = dialog_generator.DialogObject(text_without_tag_url_ownid)
        nlp_summary = dialog_obj.nlp_data.summary
        
        # モードの処理
        action, target = dialog_generator.constract_nlp(status['text'], dialog_obj)
        if userbot.mode in {'srtr', 'battle_game'}:
            action = userbot.mode
        delay_sec = 0

        p(action, text_without_tag_url_ownid, userbot.mode)
        if not is_reply and mode != 'dm':
            pass
        # mode 継承 
        elif userbot.mode == 'klepto_target':
            task = Task.select().where(Task.status == 'waiting', Task.to_whom == screen_name, Task.what == 'klepto').get()
            task.status = 'end'
            task.save()
            kleptes = task.tmptext
            userinfo.exp += 100
            ans = '[klepto-Game] \n阻止成功!!\n- @' + kleptes + ' から没収された証拠金をあなたが獲得しました。\nあなたの残EXP: ' + str(userinfo.exp)+'(+100)'
            userbot.mode = 'dialog'
            userbot.cnt = 0
        elif userbot.mode == 'ignore':
            userbot.cnt = 0
            userbot.reply_cnt = 0
            userbot.mode = 'dialog'
            ans = None
            if 'ごめん' in text:
                ans = operate_sql.get_phrase(status = 'ゆるす', n = 20, character = character)
        elif userbot.mode == 'learn.text':
            if is_reply:
                text = status['text'].replace(self.atmarked_bot_id, '')
                if 'end' in text:
                    userbot.mode = 'dialog'
                    userbot.tmp = ''
                    ans = '[学習モード]をクローズしました。この結果は開発にフィードバックされます。ご協力感謝します。'
                elif 'ttp' in text:
                    if screen_name != self.manager_id:
                        ans = '画像やURLを覚えさせるためには、管理者権限が必要です。'
                if not ans:
                    text = re.sub(r'(@[^\s　]+)', '{ID}', text)
                    labelstatus = userbot.tmp
                    if '</>' in labelstatus:
                        character, labelstatus = labelstatus.split('</>')
                    userbot.cnt = 0
                    operate_sql.save_phrase(phrase = text, author = screen_name, status = labelstatus, character = character,phrase_type = 'UserLearn')
                    ans = ''.join(['[手動学習モード] ', labelstatus, ' of ', character, ' SAVED!!...\n 続けて覚えさせるテキストをリプライしてください。\n\'end\'と入力するまでモードは続きます。'])
            else:
                ans = '[手動学習モード]の途中です。覚えさせるテキストをリプライしてください。\n\'end\'と入力するまでモードは続きます。'
        elif userbot.mode == 'make.QR':
            qrdata = status['text'].replace(self.atmarked_bot_id, '')
            file_id, filename = opencv_functions.make_qrcode(data = qrdata)
            userbot.mode = 'dialog'
            if filename:
                ans = 'QR-Codeをつくりました。(id:' + file_id + ')'
            else:
                ans = 'QR-Code作成に失敗'
        elif userbot.mode == 'harenchi':
            if userbot.cnt > 3 and np.random.rand() < 0.2:
                ans = 'ふぅ...(冷静化)'
                userbot.mode = 'dialog'
        # elif userbot.mode == 'kadai':
        #     if status['in_reply_to_screen_name'] in {self.bot_id}:
        #         text = status['text'].replace(self.atmarked_bot_id, '')
        #         text = re.sub(r'(@[^\s　]+)', '{ID}', text)
        #         if 'end' in text:
        #             userbot.mode = 'dialog'
        #             userinfo['tmp'] = ''
        #             ans = '[課題モード]CLOSED!!...\nこの結果は開発にフィードバックされます。ご協力感謝します。\n報酬として50EXP獲得\n[現在:'+ str(userinfo.exp) +'EXP]'
        #             userinfo.exp += 50
        #         else:
        #             labelstatus = userbot.tmp
        #             userbot.cnt = 0
        #             operate_sql.save_phrase(phrase = text, author = screen_name, status = labelstatus, character = 'sys',phrase_type = 'kadai.annotate')
        #             userinfo['tmp'] = np.random.choice(['好評', '苦情', '要望', '質問'])
        #             userinfo.exp += 100
        #             ans = '[課題モード] SAVED!!...報酬として100EXP獲得。\n[現在:'+ str(userinfo.exp) +'EXP]\n 次は「'+ userbot.tmp + '」のテキストをリプライしてください。e.g.) 好評 -> いいですねー\n\'end\'と入力するまでモードは続きます。'
        #     else:
        #         ans = '[課題モード]の途中です。\n\'end\'と入力するまでモードは続きます。'
        p(ans, userbot.mode)
        if ans:
            pass
        # elif nlp_summary.has_function('禁止') and nlp_summary.value:
        #     if nlp_summary.dativ:
        #         if nlp_summary.akkusativ:
        #             ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.dativ, 'に', nlp_summary.akkusativ, 'を', nlp_summary.value + 'しないであげます。'])
        #         else:
        #             ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.dativ, 'に', nlp_summary.value + 'しないであげます。'])
        #     elif nlp_summary.akkusativ:
        #         ans = ''.join([operate_sql.get_phrase(status =  'ok', character = character), '\n', nlp_summary.akkusativ, 'を', nlp_summary.value + 'しないであげます。'])
        # コマンド応答
        elif action ==  'ping':
            # ans = ''.join(['Δsec : ', str(deltasec)]) 
            ans = 'OK'     
        elif action == 'make.QR':
            userbot.mode = 'make.QR'
            ans = 'QRに変換するテキストをリプライしてください。'
        elif action == 'learn':
            userbot.mode = 'learn.text'
            tmplabel = nlp_summary.akkusativ
            try:
                chara = cmds[2]
            except:
                chara = character
            userbot.tmp = '</>'.join([chara, tmplabel])
            userbot.cnt = 0
            ans = '[学習モード]\n' + chara + 'に「' + tmplabel+ '」として覚えさせるテキストをリプライしてください。\nendと入力するまでモードは続きます。'
        elif action == 'gacha':
            picDIR = DATADIR + '/imgs/ガチャ'
            if True:
                try:
                    filename = _.getRandIMG(picDIR)
                    userinfo.exp -= 500
                    ans = operate_sql.get_phrase(status =  '勧誘チケ.success', character = character) + ' EXP -500'
                except:
                    ans = operate_sql.get_phrase(status =  '勧誘チケ.error', character = character)

        elif 'media' in status['entities'] and is_reply:
            userbot.cnt = 0
            fileID = datetime.now(JST).strftime('%Y%m%d%H%M%S')
            self.twf.give_fav(status_id)
            binary_ids = operate_sql.save_medias2db(status)
            if 'change' in action:
                if action == 'change.icon':
                    self.bot_profile.abs_icon_filename = _.saveImg(media_url = status['extended_entities']['media'][0]['media_url'].replace('_normal', ''), DIR = ''.join([DIRusers,'/',self.bot_id]), filename = '_'.join([screen_name, fileID, 'icon.jpg']))
                    ans = operate_sql.get_phrase(status =  'アイコン変更成功', character = character)
                elif action == 'change.banner':
                    self.bot_profile.abs_banner_filename =  _.saveImg(media_url = status['extended_entities']['media'][0]['media_url'].replace('_normal', ''), DIR = ''.join([DIRusers,'/',self.bot_id]), filename = '_'.join([screen_name, fileID, 'banner.jpg']))
                    ans = operate_sql.get_phrase(status =  'update.icon.banner', character = character)
                if screen_name == 'kaihatsu_paka':
                    self.bot_profile.save()
                else:
                    set_time = datetime.now(JST) + timedelta(hours=0, minutes=10)
                    operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'default', 'to_whom': screen_name, 'when':set_time, 'tmptext': ''})
                    ans = '10分間変更！！'
                self.default_profile()
            elif status['entities']['hashtags']:
                imgtag = status['entities']['hashtags'][0]['text']
                try:
                    ans = operate_sql.get_phrase(status =  'appreciate.giveme.img', character = character).format(imgtag)
                except Exception as e:
                    _.log_err()
                    ans = operate_sql.get_phrase(status =  'err.get.img', character = character)
            else:
                filename = operate_sql.db2file(_id = binary_ids[0], folderpath = None, filename = 'tmp')
                label = ''
                pic = opencv_functions.read_img(filename)
                try:
                    is_bar_detected, zbarans = opencv_functions.passzbar(pic)
                    if is_bar_detected:
                        img_kind = zbarans[0].decode('utf-8')
                        zbarans = zbarans[1].decode('utf-8')
                    else:
                        label, img_kind, image_file = machine_learning_img.predictSVM(filename  = filename, isShow = False, model = modelSVM, workDIR  = '')
                    if img_kind in {'QR-Code'}:
                        ans = zbarans
                        filename = ''
                    elif img_kind == 'anime':
                        ans = operate_sql.get_phrase(status =  'confirm.detect.img', character = character).format(label)
                        # drc = '/'.join([DIRIMGfeedback, label])
                        # if os.path.exists(drc) == False:
                        #     os.mkdir(drc)
                        # shutil.copy(filename, drc)
                        userbot.mode = 'dialog'
                        # userbot.tmpFile = '/'.join([drc, filename.split('/')[-1]])
                        filename = image_file
                    elif img_kind == 'cat':
                        ans = operate_sql.get_phrase(status =  'detect_cat', character = character)
                        filename = image_file
                    else:
                        ans = operate_sql.get_phrase(status =  'confirm.detect.img.noface', character = character).format(label)
                        filename = ''
                        userbot.mode = 'dialog'
                except:
                    _.log_err()
                    ans = ''
                if not ans:
                    ans = operate_sql.get_phrase(status =  'err.get.img', character = character)

        elif (7 + int(userbot.intimacy) /10 < userbot.reply_cnt) and mode != 'dm':
            ans = operate_sql.get_phrase(status =  '会話終了', n = 20, character = character)
            userbot.mode = 'ignore'

        # elif 'resp' in cmds_dic:
        #     try:
        #         cmds = text.split(' ')
        #         tgword = cmds[1]
        #         response = ''.join(cmds[2:])
        #         logger.debug(response)
        #         if len(tgword) > 3:
        #             # tmp['responseWord.gwor = response
        #             if operate_sql.save_phrase(phrase = response, author = screen_name, status = tgword, phrase_type = 'response'):
        #                 if tgword in self.tmp.response:
        #                     ans = 'SAVED]...' + response
        #                 else:
        #                     self.tmp.response.append(tgword)
        #                     ans = 'TL上の「' + tgword + '」をモニタリングして10分間反応します。\n 反応文を追加するには半角スペース区切りで\n response ' + tgword + ' [反応文]'
        #                     set_time = self.now + timedelta(hours=0, minutes=10)
        #                     operate_sql.save_task(taskdict = {'who':screen_name, 'what': 'del.response', 'to_whom': screen_name, 'when':set_time, 'tmptext': tgword})
        #             else:
        #                 ans = 'セー
        #         else:
        #             ans = '監視ワードは4文字以上である必要があります。'
        #     except:
        #         ans = '設定失敗。半角スペースで区切ってオーダーしてください。'
        # elif action == 'call':
        #     if nlp_summary.akkusativ is None:
        #         ans = 'えっと...だれを呼び出すのですか？'
        #     else:
        #         target_name = nlp_summary.akkusativ.replace('@', '')
        #         try:
        #             # self.twf.give_fav(status_id)
        #             # TODO] Dicをつくるべし。
        #             if target_name in {'海未', 'うみちゃん', 'うむちゃん'}:
        #                 ans = '@LiveAI_Umi'
        #             elif target_name in {'穂乃果'}:
        #                 ans = '@LiveAI_Honoka'
        #             elif target_name in {'絵里'}:
        #                 ans = '@LiveAI_Eli'
        #             elif target_name in {'花陽', 'かよちん'}:
        #                 ans = '@LiveAI_Hanayo'
        #             elif target_name in {'真姫'}:
        #                 ans = '@LiveAI_Maki'
        #             elif target_name in {'凛', '凛ちゃん'}:
        #                 ans = '@LiveAI_Rin'
        #             elif target_name in {'ちゃんあ'}:
        #                 ans = '@chana1031'
        #             elif target_name in {'ポケ海未'}:
        #                 ans = '@umi0315_pokemon'
        #             else:
        #                 ans = ''.join([nlp_summary.akkusativ, 'は呼び出しできません。'])
        #         except Exception as e:
        #             d(e, 'calling')
        #             ans = 'よびだし失敗。管理者にお問い合わせください。'
        #         else:
        #             ans = ''.join([nlp_summary.akkusativ, 'は呼び出しできません。'])
        elif 'wake' in action:
            self.twf.give_fav(status_id)
            who = self.bot_id
            set_time = nlp_summary.when
            if 'all' in action:
                who = 'all'
            operate_sql.save_task(taskdict = {'who': who, 'what': 'wake', 'to_whom': screen_name, 'when': set_time, 'tmptext': ''})
            ans = set_time.strftime('%m月%d日%H:%M') + 'に起床時間を登録しました。'
        elif action == 'send?':
            nlp_summary.dativ = self._convert_first_personal_pronoun(word = nlp_summary.dativ, convert_word = screen_name)
            if nlp_summary.akkusativ is None:
                ans = 'えっと...何を送信するのですか？'
            elif nlp_summary.dativ is None:
                ans = ''.join(['えっと...誰に', nlp_summary.akkusativ, 'を送信するのですか？'])
            else:
                ans = '送れません'
        elif 'kusoripu' in action:
            consume_exp = 100
            if 'all' in action:
                who = 'all'
                consume_exp = 2500
            if userinfo.exp < consume_exp:
                ans = 'EXPが不足しています。infomeコマンドで確認してください。'
            elif not self.twf.get_userinfo(screen_name = target)['following']:
                ans = 'そのユーザーはFF外です。送信はできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
            else:
                self.twf.give_fav(status_id)
                who = self.bot_id
                set_time = nlp_summary.when
                operate_sql.save_task(taskdict = {'who': who, 'what': 'kusoripu', 'to_whom': target, 'when': set_time, 'tmptext': screen_name})
                userinfo.exp -= consume_exp
                ans = set_time.strftime('%m月%d日%H:%M') + 'にkusoripuを登録しました。' + '\n- 残りEXP: ' + str(userinfo.exp) + '(-' + str(consume_exp) + ')'
        elif 'default' in action:
            self.twf.give_fav(status_id)
            who = self.bot_id
            if 'all' in action:
                who = 'all'
            userbot.mode = 'dialog'
            operate_sql.save_task(taskdict = {'who': who, 'what': 'default', 'to_whom':screen_name, 'when': datetime.now(JST), 'tmptext': ''})
        elif 'imitate' in action:
            consume_exp = 200
            if 'all' in action:
                who = 'all'
                consume_exp = 2000
            if userinfo.exp < consume_exp:
                ans = 'EXPが不足しています。残りEXP: ' + str(userinfo.exp)
            elif not self.twf.get_userinfo(screen_name = target)['following']:
                ans = 'そのユーザーはFF外です。imitateできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
            else:
                self.twf.give_fav(status_id)
                who = self.bot_id
                set_time = nlp_summary.when
                operate_sql.save_task(taskdict = {'who': who, 'what': 'imitate', 'to_whom':target, 'when': set_time, 'tmptext': screen_name})
                userinfo.exp -= consume_exp
                ans = set_time.strftime('%m月%d日%H:%M') + 'にimitateを登録しました。' + '\n- 残りEXP: ' + str(userinfo.exp) + '(-' + str(consume_exp) + ')'
        elif action == 'srtr':
            userbot.mode = 'srtr'
            ans = game_functions.Shiritori(text, user = screen_name).main()
            if '\END' in ans:
                ans = ans.replace('\END', '')
                userbot.mode = 'dialog'
            if '\MISS' in ans:
                ans = ans.replace('\MISS', '')
                if userbot.cnt > 3:
                    ans = operate_sql.get_phrase(status =  'shiritori.end', character = character)
                    userbot.mode = 'dialog'
                    userbot.cnt = 0
            else:
                userbot.cnt = 0
        elif action == 'battle_game':
            try:
                if userbot.mode in {'mon', 'battle_game'}:
                    enemy_name = None
                else:
                    enemy_name = nlp_summary.dativ.replace('@', '')
                if not enemy_name:
                    enemy_name = nlp_summary.akkusativ.replace('@', '')

                userbot.mode = 'battle_game'
                intext = status['text'].replace(''.join(['@', self.bot_id, ' ']), '').replace('@', '')
                battle_game = game_functions.BattleGame(screen_name, enemy_name)
                ans = '\n' + battle_game.main(intext)
                userbot.cnt = 0
                if '#END' in ans:
                    ans = ans.replace('#END', '')
                    userbot.mode = 'dialog'
                if '#MISS' in ans:
                    ans = ans.replace('#MISS', '')
                if '#exp' in ans:
                    ans, exp = ans.split('#exp')
                    userinfo.exp += 20
            except Exception as e:
                _.log_err()
                ans = '工事中...'
                userbot.mode = 'dialog'
        #----------------
        # Tell me
        elif action == 'tell?':
            if nlp_summary.akkusativ is None:
                ans = 'えっと...何をお伝えするのですか？'
            else:
                ans = nlp_summary.akkusativ + 'はお伝えできません。'
        elif action == 'tell_trendword':
            ans = '\n- '.join(['[現在のトレンドワード]'] + self.tmp.trendwords_ls[:10])
        elif action == 'tell_exp':
            ans = '\n'.join(['[現在の経験値]: ', str(userinfo.exp)])
        #----------------
        # Analyse   
        elif action == 'sentimental_analysis':
            self.twf.give_fav(status_id)
            sentiment_dic = crawling.analyse_sentiment_yahoo(word = nlp_summary.akkusativ)
            active = sentiment_dic['active']
            if active == 'negative':
                senti_icon = '😡'
            elif active == 'positive':
                senti_icon = '😊'
            else:
                senti_icon = '🐥'
            ans = '\n感情分析: {word} {senti_icon}{active}\n{posiscore}%がポジティブ\n{neutralscore}%が中立\n{negascore}%がネガティブ'.format(word = nlp_summary.akkusativ, senti_icon = senti_icon, active = active, posiscore = sentiment_dic['scores']['positive'], neutralscore = sentiment_dic['scores']['neutral'], negascore = sentiment_dic['scores']['negative'])
        #----------------
        # Omikuji
        elif action == 'omikuji':
            ans = operate_sql.get_phrase(status =  'おみくじ', n = 20, character = character)
        #----------------
        # Followback
        elif action == 'followback':
            user = self.twf.get_userinfo(screen_name = screen_name)
            if not user['following']:
                try:
                    self.twf.is_create_friendship_success(screen_name)
                    ans = operate_sql.get_phrase(status =  'followback.success', character = character)
                except:
                    ans = operate_sql.get_phrase(status =  'followback.error', character = character)
            else:
                ans = operate_sql.get_phrase(status =  'followback.already', character = character)
        #----------------
        # 診断
        elif action == 'shindanmaker':
            self.twf.give_fav(status_id)
            SM = crawling.ShindanMaker()

            try:
                url_id = [ma for ma in dialog_obj.nlp_data.mas if ma[2] == '数'][0][0]
                ans = SM.result(url = '/'.join(['https://shindanmaker.com/a', url_id]), form = ''.join(['お手伝い', self.default_character]))
            except Exception as e:
                p(e)
                SM.get_hot_shindan(n = 10)
                ans = SM.result(form = ''.join(['お手伝い', self.default_character]))
        #----------------
        # Search Func
        elif action == 'search':
            self.twf.give_fav(status_id)
            word = text.replace('#とは', '').replace(' ', '')
            ans = crawling.search_wiki(word = word)
            p(ans)
            if 'に一致する語は見つかりませんでした' in ans and not self.bot_id in status['text']:
                ans = ''
            else:
                while len(ans) > 130:
                    try:
                        ans = '。'.join(ans.split('。')[:-2])
                    except KeyboardInterrupt:
                        break
                    except:
                        _.log_err()
                ans = ''.join([ans, '。'])
                if ans == '。。':
                    ans = ''
        elif action == 'harenchi':
            if userbot.intimacy > 5:
                ans = '...ぁ//'
                userbot.mode = 'harenchi'
            else:
                ans = '？'
        elif action == 'reject':
            ans = 'お断りします。'
        elif action == 'info':
            tl_traffic = self.stats.timeline_30min_cnt / len(self.tmp.friend_ids)
            ans =  '(β)[統計情報](30min):\n- ツイ数: '+ str(self.stats.tweet_30min_cnt) + '\n- 被リプ数: ' + str(self.stats.reply_30min_cnt) + '\n- 被fav数: ' + str(self.stats.faved_30min_cnt)+ '\n- 処理TL数: ' + str(self.stats.timeline_30min_cnt) + '\n- 処理DM数: ' + str(self.stats.direct_message_30min_cnt) + '\n- traffic指数: ' + str(round(tl_traffic, 2)) + '\n- 自発確率: ' + str(round(self.rate_active_talk*100, 2)) + '%'
        elif action == 'infome':
            ans = '[ユーザー情報]\n- 「'+ self.default_character + '」との親密度: ' + str(round(userbot.intimacy, 2)) + '(Max: ' + str(round(userbot.max_intimacy, 2)) + '\n- 会話数: ' + str(userbot.total_fav_cnt) + '\n- Fav数: ' + str(userbot.total_fav_cnt) + '\n- mode: ' + userbot.mode + '\n\n- EXP: ' + str(userinfo.exp) +  '\n- 累計EXP: ' + str(userinfo.total_exp) + '\n- 累計会話数: ' + str(userinfo.total_cnt) + '\n- 累計Fav数: ' + str(userinfo.total_fav_cnt)
        elif action == 'giveto':
            give_exp = int(np.random.rand() * 100)
            transition_rate = 0.1
            with operate_sql.userinfo_with(screen_name = target) as target_userinfo:
                target_userinfo.exp += int(give_exp * (1 - transition_rate))
                transition_cost = int(give_exp * transition_rate)
            userinfo.exp -= give_exp
            ans = '\n[EXP移転]\n- あなたの残EXP: ' + str(userinfo.exp) + '\n    ↓' + str(give_exp) + 'EXP\n' + target +'の残EXP: ' + str(round(target_userinfo.exp, 2)) + '\n- 移転コスト: ' + str(int(transition_cost)) +'EXP\n- 親密度補正コスト比率'+ str(round(transition_rate *100, 2)) + '%)\n'
        elif action == 'giveme':
            rand_exp = int(np.random.rand() * 100)
            #Lose
            if np.random.rand() < 0.5:
                lost_exp = int(rand_exp / (1-(userbot.intimacy/100)))
                userinfo.exp -= lost_exp
                ans = str(lost_exp) + 'EXP喪失!!(親密度効果: '+ str(round(lost_exp / rand_exp * 100, 2)) +'%軽減)\n- 残りEXP: ' + str(userinfo.exp)
            else:
                add_exp = int(rand_exp *(1-(userbot.intimacy/100)))
                userinfo.exp += add_exp
                ans = str(add_exp) + 'EXP獲得!!(親密度効果: '+ str(round(add_exp / rand_exp * 100, 2)) +'%増大)\n- 残りEXP: ' + str(userinfo.exp)
        elif action == 'flag':
            if screen_name == 'kaihatsu_paka':
                if target in {'m'}:
                    flag_msg = 'メンテ中'
                else:
                    flag_msg = ''
                add_flag(bot_ids = [], flag = flag_msg)
                ans = None
        elif action == 'klepto':
            klepto_time = max(300, dialog_obj.nlp_data.times['total_seconds'])
            consume_exp = int(klepto_time*0.1)
            if userinfo.exp < consume_exp:
                ans = 'EXPが不足しています。残りEXP: ' + str(userinfo.exp)
            elif not self.twf.get_userinfo(screen_name = target)['following']:
                ans = 'そのユーザーはFF外です。kleptoできません。わたしをフォローするように伝えてください。わたしのフォロバが遅れている場合は、管理者に問い合わせてください。'
            elif target == screen_name:
                userinfo.exp -= consume_exp
                ans = '自分にはkleptoできません。証拠金は没収です。残りEXP: ' + str(userinfo.exp) + '(-' + str(consume_exp) + ')'
            elif mode == 'dm':
                userinfo.exp -= consume_exp
                ans = 'DMではkleptoできません。証拠金は没収です。残りEXP: ' + str(userinfo.exp) + '(-' + str(consume_exp) + ')'
            else:
                with operate_sql.userinfo_with(screen_name = target) as target_userinfo:
                    with operate_sql.userbot_with(target, self.default_character) as target_userbot:
                        userinfo.exp -= consume_exp
                        if target_userbot.mode != 'dialog':
                            ans = 'そのユーザーは特殊モード実行中です。klepto失敗。\n- 残りEXP: ' + str(userinfo.exp) + '(-' + str(consume_exp) + ')'
                        else:
                            self.twf.give_fav(status_id)
                            target_userbot.mode = 'klepto_target'
                            set_time = datetime.now(JST) + timedelta(seconds = klepto_time)
                            task = operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'klepto', 'to_whom': target, 'when': set_time, 'tmptext': screen_name, 'tmpcnt': klepto_time})
                            target_userbot.tmp = str(task.id)
                            ans = '[klepto-Game]\n@' + target + 'は、@' + screen_name + 'にEXPを狙われています。\n'+ set_time.strftime('%H:%M:%S') +'までにリプで反応できれば阻止できます。(β)\n [残り' + str(klepto_time - np.random.randint(5)) + '秒間]\n- 証拠金EXP: ' + str(consume_exp)
                            p(target_userbot.__dict__)
        elif action == 'rank':
            self.twf.give_fav(status_id)
            if not target:
                target = screen_name
            else:
                target_userinfo = operate_sql.get_userinfo(target)
                nickname = target_userinfo.nickname
            ans_ls.append(operate_sql.rank_intimacy(username = target, botname = self.default_character, nickname = nickname, is_partition = False, n = 500))
            ans_ls.append(operate_sql.rank_intimacy(username = target, botname = self.default_character, nickname = nickname, is_partition = True, n = 500))
            ans_ls.append(operate_sql.rank_exp(username =  target, user_types = ['person', 'quasi-bot'], nickname = nickname, is_totalexp = False, n = 500))
            ans_ls.append(operate_sql.rank_exp(username =  target, user_types = ['person', 'quasi-bot'], nickname = nickname, is_totalexp = True, n = 500))
        elif action == 'dict':
            self.twf.give_fav(status_id)
            ans = operate_sql.add_eitango(word = target, username = screen_name)
        elif action == 'quiz':
            quiz_tag = ['英単語']
            if target:
                quiz_tag = [target]
            ans = operate_sql.n_taku_quiz(tag = quiz_tag, form_cnt = 4)
        # その他
        elif 'NG' in text:
            self.twf.give_fav(status_id)
            ans = operate_sql.get_phrase(status =  'NGreport', character = character)
        elif 'ふぁぼ' in text:
            self.twf.give_fav(status_id)
            ans = '💓'
        elif '淫夢' in text:
            ans = operate_sql.get_phrase(status = '淫夢', character = character)
        if ans is None:
            self.twf.give_fav(status_id)
            ans = ''
            ans_ls = []
        elif not ans and not ans_ls:
            # if self.tmp.imitating != self.bot_id:
            #     ans = np.random.choice(operate_sql.get_twlog_users(n = 100, screen_name = self.tmp.imitating))
            # else:
            ans = dialog_obj.dialog(context = '', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = [], BlackList = [], min_similarity = 0.2, character = character, tools = 'SS,MC', username = '@〜〜')
            ans = ans.replace('<人名>', status['user']['name']).replace(self.atmarked_bot_id, '')
            if not ans:
                ans = '...'

        if is_new_user_forsystem:
            p('detected_new_user')
            user = self.twf.get_userinfo(screen_name = screen_name)
            userinfo.name = user['name']
            userinfo.user_id = user['id_str']
            userinfo.status_id = user['status']['id_str']
            if not user['following']:
                welcomeans = operate_sql.get_phrase(status =  'welcomeNewUser', character = character)
                try:
                    self.twf.is_create_friendship_success(screen_name)
                except:
                    welcomeans = operate_sql.get_phrase(status =  'followback.error', character = character)
            else:
                welcomeans = operate_sql.get_phrase(status =  'welcome.NEWscreen_name', character = character)
            if not welcomeans:
                welcomeans = 'NEW_USER登録完了！！システムに登録しました。\n(ID変更の際も発生するメッセージです。引き継ぎの場合には、開発者まで。)'
                ans_ls.append(welcomeans)
        if ans:
            ans_ls.append(ans)
        if ans_ls:
            for ans in ans_ls:
                if userbot.mode == 'harenchi':
                    ans = dialog_generator.Conv.aegi(ans)
                if delay_sec > 0:
                    set_time = self.get_time(hours = 0, seconds =  delay_sec)
                    operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': '  tweet', 'to_whom': screen_name, 'when':set_time, 'tmpid': status_id, 'tmptext': ans})
                else:
                    tweet_status = self.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = mode)
                userbot.context = '</>'.join([userbot.context, ans])
        return tweet_status

    @_.forever(exceptions = Exception, is_print = False, is_logging = True, ret = False)
    def is_ignore(self, status):
        if status['retweeted']:
            return True
        if status['is_quote_status']:
            return True
        screen_name = status['user']['screen_name']
        if screen_name in self.response_exception_set:
            return True
        if screen_name == self.bot_id:
            return True
        if any([ng_word in status['text'] for ng_word in ['RT', 'QT', '【', 'ポストに到達', 'リプライ数']]):
            if status['mode'] != 'dm':
                return True
        # if 'LiveAI_' in screen_name:
        #     return True
        return False

    def monitor_timeline(self, status):
        ''''
        タイムラインを監視し、学習あるいは反応ツイートする。return Trueで停止
        一時休止中
        '''
        ans = ''
        ans_ls = []
        text = status['clean_text']
        screen_name = status['user']['screen_name']
        filename = ''       
        if status['user']['screen_name'] == 'eewbot':
            screen_name = ''
            ans = self.response_eew(csv = text, standard = 0)
            self.send(ans, screen_name = screen_name, status_id = status['id_str'], imgfile = filename, mode = 'tweet')
            return True
        elif status['entities']['urls']:
            return True
        elif is_kusoripu(status['text']):
            rand = np.random.rand()
            p('kusoripu', rand, status['text'])
            if rand < 0.2:
                with operate_sql.userinfo_with(screen_name) as userinfo:
                    ans = operate_sql.get_kusoripu(tg1 = screen_name, is_open = False)
                    userinfo.status_id = status['id_str']
                    # if not 'select_chara' in userinfo._data:
                    if userinfo.talk_with == self.default_character:
                        self.send(ans, screen_name = screen_name, status_id = status['id_str'], imgfile = filename, mode = 'tweet')
                        # operate_sql.save_phrase(phrase = re.sub(r'(@[^\s　]+)', '{ID}', status['text']), author = screen_name, status = 'kusoripu', character = self.bot_id, phrase_type = 'AutoLearn')
            return True
        elif status['in_reply_to_screen_name'] in {None, self.bot_id}:
            special_response_word = _.crowlList(text = text, dic = self.tmp.response)
            if special_response_word:
                p(special_response_word)
                ans = operate_sql.get_phrase(status =  special_response_word, character= self.default_character)
            else:
                text = _.clean_text2(text)
                mas = natural_language_processing.MA.get_mecab_ls(text)
                ans = dialog_generator.extract_haiku(mas)
        # #ツイート
        if ans:
            ans_ls.append(ans)
        if ans_ls:
            for ans in ans_ls:
                with operate_sql.userinfo_with(screen_name) as userinfo:
                    userinfo.status_id = status['id_str']
                    if userinfo.talk_with == self.default_character:
                        self.send(ans, screen_name = screen_name, status_id = status['id_str'], imgfile = filename, mode = 'tweet')
            return True
        return False

    @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = False)
    def is_react(self, status):
        '''
        タイムライン上のどのツイートに反応するかを決める関数
        '''
        text = status['clean_text']
        if self.stats.tweet_30min_cnt > 50:
            # if self.bot_id in status['text']:
            #     self.twf.give_fav(status['id_str'])
            return False
        elif self.bot_id in status['text']: #リプライ全応答。
            self.stats.reply_30min_cnt += 1
            return True
        elif 'LiveAI_' in status['text']:
            return False
        elif iscalledBOT(text = text, select_set = {self.default_character}):
            return True
        elif '#とは' in status['text']:
            with operate_sql.userinfo_with(status['user']['screen_name']) as userinfo:
                if self.default_character == userinfo.talk_with:
                    return True
        rand = np.random.rand()
        if any(['bot' in name for name in {status['user']['screen_name'], status['user']['name']}]):
            if rand < 0.1* self.rate_active_talk: #BOTに対する自発。0.1%
                return True
        elif rand < self.rate_active_talk: #自発。1%
            return True
        return False

    @_.forever(exceptions = Exception, is_print = True, is_logging = True)
    def on_status_main(self, status):
        # ステータスIDをリストへ入れる。 定期取得時に重複を省くため
        # self.status_ids.append(status['id_str'])
        self.stats.timeline_30min_cnt += 1
        # status_sql, is_created = TweetStatus.create_or_get(_id = status['id_str'], data = status)
        operate_sql.save_tweet_status(status, is_display = True)
        # p(status_sql._id, is_created)
        status['mode'] = 'timeline'
        if not self.is_ignore(status):
            status['clean_text'] = _.clean_text(status['text'])
            #直近ツイート処理
            if self.monitor_timeline(status):
                return True
            # リアクション
            if self.is_react(status):
                with operate_sql.userinfo_with(status['user']['screen_name']) as userinfo:
                    if userinfo.status_id != status['id_str']:
                        # status_idの更新
                        userinfo.status_id = status['id_str']
                    else:
                        #同一status_idへは返答しない。
                        return True
                    # talkwithがキャラと異なる場合
                    if userinfo.talk_with != self.default_character:
                        # 自発だったら、取りやめる。
                        if not self.bot_id in status['text']:
                            return True
                        # 話しかけられたら、talkwith更新
                        else:
                            userinfo.talk_with = self.default_character
                    with operate_sql.userbot_with(status['user']['screen_name'], userinfo.talk_with) as userbot:
                        if not self.bot_id in status['text']:
                            if userbot.mode != 'dialog':
                                return True
                        # 返信か否かの判定
                        if userbot.reply_id != status['in_reply_to_status_id_str']:
                            userbot.context = ''
                            userbot.reply_cnt = 0
                        else:
                            # 返信のとき
                            userbot.intimacy = mod_intimacy(userbot.intimacy, is_increase = True)
                            userbot.reply_cnt += 1
                        userbot.cnt += 1
                        userinfo.total_cnt += 1
                        userinfo.time = datetime.now(JST)
                        userbot.time = userinfo.time
                        userinfo.exp += 10
                        tweet_status = self.main(status, mode = 'tweet', userinfo = userinfo, userbot = userbot)
                        if hasattr(tweet_status, 'id_str'):
                            userinfo.reply_id = tweet_status.id_str
                            userbot.reply_id = tweet_status.id_str
    @_.forever(exceptions = Exception, is_print = True, is_logging = True)
    def on_direct_message_main(self, status):
        self.stats.direct_message_30min_cnt += 1
        status = status['direct_message']
        try:
            DMStatus.create(_id = status['id_str'], data = status)
        except:
            pass
        status['mode'] = 'dm'
        status['user'] = {}
        status['user']['screen_name'] = status['sender_screen_name']
        status['user']['name'] = status['sender']['name']
        status['user']['id_str'] = status['sender']['id_str']
        status['in_reply_to_status_id_str'] = None
        status['in_reply_to_screen_name'] = self.bot_id
        status['extended_entities'] = status['entities']
        status['retweeted'] = False
        status['is_quote_status'] = False
        if not self.is_ignore(status):
            #ツイートステータス情報追加処理
            status['clean_text'] = _.clean_text(status['text'])
            with operate_sql.userinfo_with(status['user']['screen_name']) as userinfo:
                with operate_sql.userbot_with(status['user']['screen_name'], self.default_character) as userbot:
                    tweet_status = self.main(status, mode = 'dm', userinfo = userinfo, userbot = userbot)
                    userbot.cnt += 1
                    userinfo.total_cnt += 1
                    userbot.reply_cnt += 1
                    userbot.intimacy = mod_intimacy(userbot.intimacy, is_increase = True)
                    userinfo.time = datetime.now(JST)
                    userbot.time = userinfo.time
                    userinfo.exp += 10
        return True
    @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = True)
    def on_event_main(self, status):
        try:
            EventStatus.create(data = status)
        except:
            pass
        if status['event'] == 'favorite':
            if status['target']['screen_name'] == self.bot_id:
                self.stats.faved_30min_cnt += 1
                with operate_sql.userinfo_with(status['source']['screen_name']) as userinfo:
                    with operate_sql.userbot_with(status['source']['screen_name'], self.default_character) as userbot:
                        userinfo.total_fav_cnt += 1
                        userbot.total_fav_cnt += 1
                        userinfo.time = datetime.now(JST)
                        userbot.time = userinfo.time
                        userinfo.exp += 10
                        userbot.intimacy = mod_intimacy(userbot.intimacy, is_increase = True)
        elif status['event'] == 'unfavorite':
            if status['target']['screen_name'] == self.bot_id:
                self.stats.faved_30min_cnt -= 1
                with operate_sql.userinfo_with(status['source']['screen_name']) as userinfo:
                    with operate_sql.userbot_with(status['source']['screen_name'], self.default_character) as userbot:
                        userinfo.total_fav_cnt -= 1
                        userbot.total_fav_cnt -= 1
                        userinfo.time = datetime.now(JST)
                        userbot.time = userinfo.time
                        userinfo.exp -= 10
                        userbot.intimacy = mod_intimacy(userbot.intimacy, is_increase = False)
        elif status['event'] == 'quoted_tweet':
            p(status)
            if status['target']['screen_name'] == self.bot_id:
                with operate_sql.userinfo_with(status['source']['screen_name']) as userinfo:
                    with operate_sql.userbot_with(status['source']['screen_name'], self.default_character) as userbot:
                        userinfo.time = datetime.now(JST)
                        userbot.time = userinfo.time
                        userinfo.exp += 10
                        userbot.intimacy = mod_intimacy(userbot.intimacy, is_increase = True)
        elif status['event'] == 'unfollow':
            if status['target']['screen_name'] == self.bot_id:
                screen_name = status['source']['screen_name']
                p(screen_name)
                if self.twf.is_destroy_friendship_success(screen_name = screen_name):
                    return True
        elif status['event'] == 'follow':
            if status['target']['screen_name'] == self.bot_id:
                userobject = status['source']
                if self.check_if_follow(userobject):
                    if self.twf.is_create_friendship_success(screen_name = status['source']['screen_name']):
                        return True
        elif status['event'] == 'user_update':
            if status['target']['screen_name'] == self.bot_id:
                if not status['source']['location'] is None:
                    if 'マネ' in status['source']['location']:
                        return True
                self.bot_profile.name = status['source']['name']
                self.bot_profile.description = status['source']['description']
                self.bot_profile.url = status['source']['url']
                self.bot_profile.id_str = status['source']['id_str']
                self.bot_profile.location = status['source']['location']
                self.bot_profile.save()
        else:
            p(status)
        return True

    @_.forever(exceptions = Exception, is_print = True, is_logging = True, ret = False)
    def check_if_follow(self, userobject):
        if userobject['lang'] != 'ja':
            return False
        if userobject['statuses_count'] < 100:
            return False
        if userobject['favourites_count'] < 20:
            return False
        if userobject['followers_count'] > 5000:
            return True
        elif userobject['followers_count'] == 0:
            return False
        if userobject['friends_count'] == 0:
            return False
        ff_rate = userobject['followers_count'] / userobject['friends_count']
        if ff_rate < 0.7:
            if (userobject['listed_count'] / userobject['followers_count']) < 0.02:
                return False
        return True

    @_.forever(exceptions = Exception, is_print = False, is_logging = True, ret = True)
    def implement_tasks(self, task):
        @_.forever(exceptions = Exception, is_print = False, is_logging = True, ret = True)
        def task_restart():
            duration_min = int(task['tmptext'])
            postmin = self.get_time(minutes = duration_min)
            # operate_sql.update_task(who_ls = [self.bot_id], kinds = [task['what']], taskdict = {'status': 'end'})
            operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': task['what'], 'to_whom': '', 'when':postmin, 'tmptext': task['tmptext']})
        ans = ''
        taskid = task['id']
        todo = task['what']
        screen_name = task['to_whom']
        filename = task['tmpfile']
        status_id = task['tmpid']
        set_time = task['when']
        try_cnt = 0
        p(self.bot_id, todo)

        if not operate_sql.update_task(taskid = taskid, taskdict = {'status': 'end'}):
            return

        if todo == 'timer':
            ans = datetime.strftime(set_time, '%m月%d日 %H時%M分%S秒') + 'です。タイマーの時刻を経過しました。\n' + task['tmptext']
        elif todo == 'tweet':
            ans = task['tmptext']
            try_cnt = task['tmpcnt']
        elif todo == 'wake':
            ans = operate_sql.get_phrase(status =  'おはよう', character = character)
        elif todo == 'kusoripu':
            try:
                ans = operate_sql.get_kusoripu(tg1 = screen_name, is_open = False)
            except Exception as e:
                _.log_err()
                ans = 'クソリプ失敗。管理者にお問い合わせください。'
        elif todo == 'imitate':
            target = screen_name
            try:
                if self.twf.imitate(target):
                    ans = operate_sql.get_phrase(status =  'imitate.success', character = character).format(''.join(['@', target, ' ']))
                    mode = 'open'
                    screen_name = task['tmptext']
                    self.tmp.imitating = target
                    set_time = datetime.now(JST) + timedelta(hours=0, minutes=10)
                    operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': 'default', 'to_whom':screen_name, 'when':set_time, 'tmptext': ''})
                else:
                    ans = operate_sql.get_phrase(status =  'imitate.error.notFF', character = character).format(''.join(['@', target, ' ']))
            except Exception as e:
                _.log_err()
                ans = 'imitation失敗。管理者にお問い合わせください。'
        elif todo == 'default':
            if self.default_profile():
                self.tmp.imitating = self.bot_id
                ans = 'デフォルトに戻りました'
            else:
                ans = 'デフォルトに戻るのに失敗 サポートにお問い合わせください。'
        # elif todo == 'teiki':
        #     ans = operate_sql.get_phrase(status = 'teiki', n = 100, character= self.default_character)
        #     post20min = self.get_time(minutes = 30)
        #     operate_sql.update_task(who_ls = [self.bot_id], kinds = [todo], taskdict = {'status': 'end'})
        #     operate_sql.save_task(taskdict = {'who':self.bot_id, 'what': todo, 'to_whom': '', 'when':post20min})
        elif todo == 'teikiMC':
            ans = ''
            trigram_markov_chain_instance = dialog_generator.TrigramMarkovChain(self.default_character)
            ans = trigram_markov_chain_instance.generate(word = '', is_randomize_metasentence = True)
            ans = ans.replace(self.atmarked_bot_id, '')
            if np.random.rand() < 0.05:
                ans = dialog_generator.Conv.aegi(ans)
            task_restart()
        elif todo == 'teiki.trendword':
            trendwords = self.twf.getTrendwords()
            trendword = np.random.choice(trendwords)
            sentiment_dic = crawling.analyse_sentiment_yahoo(word = trendword)
            if sentiment_dic:
                active = sentiment_dic['active']
                if active == 'negative':
                    senti_icon = '😡'
                elif active == 'positive':
                    senti_icon = '😊'
                else:
                    senti_icon = '🐥'
                ans = '「{trendword}」{senti_icon}({score}%)'.format(trendword = trendword, senti_icon = senti_icon, active = active, score = sentiment_dic['scores'][active])
        #     ans = operate_sql.get_phrase(status = 'トレンドワード', character= self.default_character).format(trendword)
            self.tmp.trendwords_ls = trendwords
            task_restart()
        elif todo == 'followback_check':
            followers = self.twf.get_followers_all(self.bot_id)
            not_followbacked_followers_objects = [obj._json for obj in followers if obj._json['following'] != True and self.check_if_follow(obj._json)]
            if not_followbacked_followers_objects:
                objects_cnt = len(not_followbacked_followers_objects)
                rand_objs = random.sample(not_followbacked_followers_objects, min(objects_cnt, 10))
                for userobject in rand_objs:
                    target_name = userobject['screen_name']
                    p('followback implementation: ', target_name)
                    try:
                        self.twf.is_create_friendship_success(screen_name = target_name)
                    except Exception as e:
                        d(target_name, e)
                        _.log_err()
                        pass
                    finally:
                        time.sleep(10)
            task_restart()
        elif todo == 'update.lists':
            userinfo_me = self.twf.twtr_api.me()
            bot_id = userinfo_me.screen_name
            self.bot_id = bot_id
            self.bots_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'BOT'))
            self.response_exception_set = set(self.twf.get_listmembers_all(username = self.bot_id, listname = 'responseException'))
            task_restart()
        elif todo == 'del.response':
            try:
                self.tmp.response.remove(task['tmptext'])
            except:
                logger.debug('del err')
        elif todo == 'save_stats':
            operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'tweet_30min_cnt', 'number': self.stats.timeline_30min_cnt})
            operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'reply_30min_cnt', 'number': self.stats.reply_30min_cnt})
            operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'time_line_cnt', 'number': self.stats.timeline_30min_cnt})
            operate_sql.save_stats(stats_dict = {'whose': self.bot_id, 'status': 'direct_message_30min_cnt', 'number': self.stats.direct_message_30min_cnt})
            # 自発確率の自動調整
            orig_rate = self.rate_active_talk
            if self.stats.tweet_30min_cnt < 40:
                self.rate_active_talk *= 1.1
            else:
                self.rate_active_talk /= 1.1
            # TL混雑
            tl_traffic = self.stats.timeline_30min_cnt / len(self.tmp.friend_ids)
            if tl_traffic > 1.3:
                self.rate_active_talk *= 1.05
            else:
                self.rate_active_talk /= 1.05
            # 上限設定
            max_rate_active_talk = 0.05
            if self.rate_active_talk > max_rate_active_talk:
                self.rate_active_talk = max_rate_active_talk
            rate_inc = round(self.rate_active_talk / orig_rate, 2)
            ans = '@LiveAI_Alpaca (β)[統計情報](30min):\n- ツイ数: '+ str(self.stats.tweet_30min_cnt) + '\n- 被リプ数: ' + str(self.stats.reply_30min_cnt) + '\n- 被fav数: ' + str(self.stats.faved_30min_cnt)+ '\n- 処理TL数: ' + str(self.stats.timeline_30min_cnt) + '\n- 処理DM数: ' + str(self.stats.direct_message_30min_cnt) + '\n- traffic指数: ' + str(round(tl_traffic, 2)) + '\n- 自発確率: ' + str(round(self.rate_active_talk*100, 2)) + '(x'+ str(rate_inc) + ')'
            self.stats.tweet_30min_cnt = 0
            self.stats.reply_30min_cnt = 0
            self.stats.faved_30min_cnt = 0
            self.stats.fav_30min_cnt = 0
            self.stats.timeline_30min_cnt = 0
            self.stats.direct_message_30min_cnt = 0
            task_restart()
        elif todo == 'hot_shindan_maker':
            SM = crawling.ShindanMaker()
            SM.get_hot_shindan(n = 10)
            ans = SM.result(form = ''.join(['お手伝い', self.default_character]))
            task_restart()
        elif todo == 'klepto':
            target = screen_name
            kleptes = task['tmptext']
            with operate_sql.userinfo_with(screen_name = kleptes) as kleptes_userinfo:
                with operate_sql.userinfo_with(screen_name = target) as target_userinfo:
                    with operate_sql.userbot_with(username = target, botname = self.default_character) as target_userbot:
                        target_userbot.mode = 'dialog'
                        stolen_exp = int(task['tmpcnt'] /10)
                        target_userinfo.exp -= stolen_exp
                        kleptes_userinfo.exp += stolen_exp + 100
                        ans = '[klepto-Game] \n' + str(stolen_exp) + 'EXPを@' + target + 'から盗むのに成功!!' + '\n- ' + kleptes_userinfo.nickname + 'の残EXP: ' + str(kleptes_userinfo.exp) + '\n    ↑' + str(stolen_exp) + 'EXP\n' + target_userinfo.nickname +'の残EXP: ' + str(round(target_userinfo.exp, 2))
                        screen_name = kleptes
        elif todo == 'update_userprofile':
            userobj = self.twf.twtr_api.me()
            if hasattr(userobj, 'location'):
                if not 'マネ' in userobj.location:
                    self.bot_profile = self.twf.download_userobject_urls(userobj, target_object = self.bot_profile, DIR = DIRusers)
                    self.bot_profile.save()
            task_restart()
            pass
        else:
            pass
        #Answer
        if ans:
            self.send(ans, screen_name = screen_name, imgfile = filename, status_id = status_id, mode = 'tweet', try_cnt = try_cnt)
        return True
    def get_time(self, hours = 0, minutes = 5, seconds = 0):
        rand_time = datetime.now(JST) + timedelta(hours = hours, minutes = minutes, seconds = seconds)
        return rand_time
    def initialize_tasks(self):
        operate_sql.update_task(who_ls = [self.bot_id], kinds = ['tweet', 'teiki', 'teikiMC', 'teiki.trendword', 'teiki_recheck', 'erase.tmp.stats.tweet_30min_cnt', 'update.lists', 'default','update_userprofile','save_stats', 'followback_check', 'hot_shindan_maker'], taskdict = {'status': 'end'})
        # operate_sql.del_tasks('end')
        # operate_sql.del_tasks('waiting')
        task_duration_dic = {
            # 'teiki': 30,
            'teikiMC': 20,
            'teiki.trendword': 120,
            'teiki_recheck': 1,
            'followback_check': 30,
            'update.lists': 30,
            'update_userprofile' : 10,
            'save_stats': 30,
            'hot_shindan_maker': 120
            }
        def save_task(task_name, duration_min):
            rand_start_min = np.random.randint(0, 20)
            operate_sql.save_task(taskdict = {'who': self.bot_id, 'what': task_name, 'to_whom': '', 'tmptext': str(duration_min), 'when': self.get_time(minutes = rand_start_min)})
        [save_task(task_name, duration_min) for task_name, duration_min in task_duration_dic.items()]

##############
# Main Functions
##############
def monitor(bots, q, lock):
    async def task_manage(period = 60):
        await asyncio.sleep(120)
        while True:
            try:
                now = datetime.utcnow() + timedelta(hours = 9)
                tasks = operate_sql.search_tasks(when = now, n = 100)
                p('TASK', now)
                if tasks:
                    try:
                        for task in tasks:
                            if task.who == 'all':
                                for bot in bots.values():
                                    task_thread = threading.Thread(target = bot.srf.implement_tasks, args=(task._data, ), name = task.who +' do_task', daemon = True)
                                    task_thread.start()
                            elif task.who in bots:
                                task_thread = threading.Thread(target = bots[task.who].srf.implement_tasks, args=(task._data, ), name = task.who +' do_task', daemon = True)
                                task_thread.start()
                    except:
                        _.log_err()
                await asyncio.sleep(period)
            except KeyboardInterrupt:
                break
            except:
                _.log_err()
    async def db_manager(period = 600):
        while True:
            try:
                await asyncio.sleep(period)
                #endのタスクを消去
                operate_sql.del_tasks(status = 'end')
                #現在数値とmax値を比較し、max値を更新
                operate_sql.adjust_userbot_max_value()
                operate_sql.adjust_userbot_max_value()
                #10分ごとに親密度目減り
                userbots = operate_sql.get_userbot_bytime(delay_min = 10)
                for userbot in userbots:
                    userbot.tmp = ''
                    userbot.cnt = 0
                    userbot.reply_cnt = 0
                    userbot.context = 0
                    userbot.mode = 'dialog'
                    userbot.intimacy = max(float(userbot.max_intimacy)*0.6, float(userbot.intimacy) / 1.0005)
                    userbot.save()
            except KeyboardInterrupt:
                break
            except:
                _.log_err()
    async def restarter(period = 1200):
        while True:
            try:
                await asyncio.sleep(period)
                for bot_id, bot in bots.items():
                    await asyncio.sleep(30)
                    bot.restart()
            except KeyboardInterrupt:
                break
            except:
                _.log_err()

    async def thread_checker(period = 60):
        while True:
            try:
                await asyncio.sleep(period)
                # print(threading.enumerate())
                for bot_id, bot in bots.items():
                    print('checking '+ bot.bot_thread.name)
                    if not bot.bot_thread.is_alive():
                        bot.restart()
                    elif not bot.events.ping.is_set():
                        bot.restart()
                    else:
                        bot.events.ping.clear()
                        print(bot.bot_thread.name + ' thread is active...')
            except KeyboardInterrupt:
                break
            except:
                _.log_err()


    async def reconnect_wifi_async(period = 60, force = False):
        await asyncio.sleep(180)
        while True:
            try:
                await asyncio.sleep(period)
                # reconect algorithm
                # check ping to google.com
                if _.Ping('google.com').is_connectable:
                    p('ping is connecting. reconnect-program -> finished!!!!')
                    if not force:
                        return True
                # variables
                networksetup_cmd = '/usr/sbin/networksetup'
                optionargs = ['off']
                args = [networksetup_cmd, '-setairportpower', 'en0']
                i = 0
                # while loop to reconnect Internet
                while True:
                    p('reconnection retry_cnt:', i)
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
                    await asyncio.sleep(2)
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
                    p('reconnecting wifi, wait 10sec...')
                    p('checking ping...')
                    await asyncio.sleep(10)
                    # re-ping to check the Internet connection
                    if _.Ping('google.com').is_connectable:
                      p('ping is connecting. reconnect-program -> finished!!!!')
                      break
                    else:
                      p('ping is NOT connecting... restart -> reconnect-program...')
                      await asyncio.sleep(2)
                return True
            except KeyboardInterrupt:
                break
            except:
                _.log_err()
    async def _test(period = 20):
        print('test')
        await asyncio.sleep(period)
    #
    process = multiprocessing.current_process()
    print('starting '+ process.name)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # asyncio.ensure_future(multi_fetch(q, lock))
    asyncio.ensure_future(task_manage(period = 10))
    asyncio.ensure_future(restarter(period = 1800))#1800
    asyncio.ensure_future(thread_checker(period = 60))#1800
    asyncio.ensure_future(reconnect_wifi_async(period = 60))
    asyncio.ensure_future(db_manager(period = 600))
    try:
        loop.run_forever()
    except:
        _.log_err()
    finally:
        loop.close()
        print('end')

def add_flag(bot_ids = [], flag = 'メンテ中'):
    for bot_id in bot_ids:
        twf = twtr_functions.TwtrTools(bot_id)
        bot_profile = operate_sql.BotProfile(bot_id)
        twf.update_profile(name = '@'.join([bot_profile.name, flag]), description = bot_profile.description, location= flag, url = bot_profile.url, filename = bot_profile.abs_icon_filename, BGfilename = '', Bannerfilename = bot_profile.abs_banner_filename)

def init_srfs(bots, lock):
    def _init_srf(bot_id):
        try:
            return bot_id, StreamResponseFunctions(bot_id, lock)
        except:
            _.log_err()
    srfs = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [loop.run_in_executor(None, _init_srf, bot_id) for bot_id in bots]
    try:
        done, pending = loop.run_until_complete(asyncio.wait(tasks))
        for d in done:
            bot_id, srf = d.result()
            srf.initialize_tasks()
            srfs[bot_id] = srf
    finally:
        loop.close()
        return srfs

class LiveAI_Async(MyObject):
    def __init__(self, bot_id, srfs, q, lock):
        self.bot_id = bot_id
        self.twf = twtr_functions.TwtrTools(bot_id)
        self.srfs = srfs
        self.srf = self.srfs[self.bot_id]
        self.q = q
        self.lock = lock
        self.events = Temp()
        self.events.stop = threading.Event()
        self.events.ping = threading.Event()
        self.bot_thread = threading.Thread(target = self.twf.user_stream, args=(self.srf, self.q, self.lock, self.events), name = self.bot_id, daemon = True)
    def run(self):
        p(self.bot_thread.name + ' running thread')
        self.bot_thread.start()
    def stop(self):
        p(self.bot_thread.name + ' stopping thread')
        self.events.stop.set()
        self.bot_thread.join()
        self.events.stop.clear()
        p(self.bot_thread.name + ' has stop thread')
    def restart(self):
        p(self.bot_thread.name + ' restarting thread')
        self.stop()
        if not self.bot_thread.is_alive():
            p(self.bot_thread.name + ' restarting cloning thread')
            self.bot_thread = threading.Thread(target = self.twf.user_stream, args=(self.srf, self.q, self.lock, self.events), name = self.bot_id, daemon = True)
            self.run()
        else:
            p(self.bot_thread.name + ' is active.. err')

def main(cmd = 1):
    from collections import deque
    dq = deque()
    lock = threading.Lock()
    bot_ids = ['LiveAI_Alpaca']
    if cmd > 0:
        bot_ids = ['LiveAI_Umi', 'LiveAI_Honoka', 'LiveAI_Kotori', 'LiveAI_Maki', 'LiveAI_Rin', 'LiveAI_Hanayo', 'LiveAI_Nozomi', 'LiveAI_Eli', 'LiveAI_Nico']
    if cmd > 1:
        bot_ids += ['LiveAI_Yukiho', 'LiveAI_Alisa', 'LiveAI_Yoshiko', 'LiveAI_Riko', 'LiveAI_You', 'LiveAI_Chika', 'LiveAI_Ruby','LiveAI_Mari', 'LiveAI_Kanan', 'LiveAI_Hanamaru']
    # operate_sql.del_tasks('end')
    # operate_sql.del_tasks('waiting')
    srfs = init_srfs(bot_ids, lock)
    bots = {}
    for bot_id in bot_ids:
        bot = LiveAI_Async(bot_id, srfs, dq, lock)
        bots[bot_id] = bot
        bot.run()
    monitor(bots, dq, lock)
if __name__ == '__main__':
    main(3)
    # get_kusoripu
    # p(mod_intimacy(1, is_increase = True))

    # trendword = 'スクフェス'
    # sentiment_dic = crawling.analyse_sentiment_yahoo(word = trendword)
    # active = sentiment_dic['active']
    # if active == 'negative':
    #     senti_icon = '😡'
    # elif active == 'positive':
    #     senti_icon = '😊'
    # else:
    #     senti_icon = '🐥'
    # ans = 'トレンドワード感情分析: {trendword} {senti_icon}\n{score}%が{active}'.format(trendword = trendword, senti_icon = senti_icon, active = active, score = sentiment_dic['scores'][active])
    # p(ans)
    # trigram_markov_chain_instance = dialog_generator.TrigramMarkovChain('雪穂')
    # ans = trigram_markov_chain_instance.generate(word = '', is_randomize_metasentence = True)
    # p(ans)

























