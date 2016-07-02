
#!/usr/bin/env python
# -*- coding: utf-8 -*-
##______________________
## MeCabによる形態素解析 //
# import MeCab
import subprocess
import re
from itertools import chain
import _
from _ import p, d, MyObject, MyException

class RegexTools(MyObject):
    def __init__(self):
        pass
    def extract_kaomojis(self, s):
        text = '[0-9A-Za-zぁ-ヶ一-龠]'
        non_text = '[^0-9A-Za-zぁ-ヶ一-龠]'
        allow_text = '[ovっつ゜ニノ三二]'
        hw_kana = '[ｦ-ﾟ]'
        open_branket = '[\(∩꒰（]'
        close_branket = '[\)∩꒱）]'
        arround_face = ''.join(['(?:', non_text, '|', allow_text, ')*'])
        face = ''.join(['(?!(?:', text, '|', hw_kana, '){3,}).{3,}?'])
        face_char = re.compile(''.join([arround_face, open_branket, face,   close_branket, arround_face]))
        facelist = face_char.findall(s)
        cleaned = re.sub(face_char, '(^ ^)' , s)
        return cleaned, facelist
    def extract_ids(self, s):
        reg = '@[a-zA-Z0-9_]+'
        compiled_reg = re.compile(reg, re.M)
        rest_text = re.sub(compiled_reg, 'atmarkedID', s)
        ex_ls = compiled_reg.findall(s)
        return rest_text, ex_ls
    def extract_specific_words(self, s):
        spe_char = re.compile('\s{1,2}(\w{1,}?)\s{1,2}');
        ex_ls = spe_char.findall(s)
        extracted_rest = re.sub(spe_char, '<EX>' , s)
        return extracted_rest, ex_ls
    def extract_param(self, text, src_ls):
        try:
            eq_ls = ['=', '＝', ':', '：']
            if any([eq in text for eq in eq_ls]):
                reg = ''.join(['(\w+)\s*['] + eq_ls + [']\s*[@#]*(\w+)'])
                compiled_reg = re.compile(reg, re.M)
                reg_ls = compiled_reg.findall(text)
                reg_pair = reg_ls[0]
                return reg_pair[0], reg_pair[1]
            else:
                param_num = src_ls.index(text)
                return '<key{}>'.format(str(param_num)), text
        except Exception as e:
            p(e)
            return '', text
    # def extract_commas(self, src_ls):
    #     try:
    #         params = src_ls[1]
    #         comma_cnt = params.count(',')
    #         reg_comma = ''.join(['\s*[@#]*(.+)\s*', ',\s*[@#]*(.+)\s*' * comma_cnt])
    #         compiled_reg_comma = re.compile(reg_comma, re.M)
    #         reg_comma_ls = compiled_reg_comma.findall(params)
    #         if isinstance(reg_comma_ls[0], str):
    #             reg_comma_ls = [reg_comma_ls]
    #         return {pair_set[0]: pair_set[1] for pair_set in [self.extract_param(param, reg_comma_ls[0]) for param in reg_comma_ls[0]]}
    #     except:
    #         pass
    # def extract_cmds_dic(self, text):
    #     try:
    #         if '(' in text and ')' in text:
    #             reg = '\s*([a-zA-Z_]+)\s*\(([^\)\)]*)\)'
    #         else:
    #             reg = '\s*([a-zA-Z_]+)\s*\s([^=\s]+?)[\s,]'
    #         compiled_reg = re.compile(reg, re.M)
    #         reg_ls = compiled_reg.findall(text)
    #         text = re.sub(compiled_reg, '', text)
    #         #-- と空白で挟まれたものをコマンドにする
    #         return {reg[0]: self.extract_commas(reg) for reg in reg_ls}, text
    #         # return {reg[0]: {sets[0]: sets[1] for sets in [extract_param(param, reg[1]) for param in reg[1:]]} for reg in reg_ls}, text
    #     except Exception as e:
    #         p(e)
    #         return {}, text
    def complie_and_get_groupdict(self, reg, text = None):
            if text is None:
                text = ''
            compiled_reg = re.compile(reg, re.M)
            reg_ls = compiled_reg.search(text)
            if reg_ls:
                reg_ls_groupdict = reg_ls.groupdict()
            else:
                reg_ls_groupdict = {}
            return reg_ls_groupdict
    def complie_and_get_groupdict_all(self, reg, text = None):
            if text is None:
                text = ''
            compiled_reg = re.compile(reg, re.M)
            iterator = compiled_reg.finditer(text)
            groupdict = []
            for match in iterator:
                groupdict.append(match.groupdict())
            return groupdict
    def extract_discorse(self, text):
            reg =  '(?P<person>\w{0,10}?)\s{0,3}(?P<text>((『[^『』]*?』)|(＜[^＜＞]*?＞)|(（[^（）]*?）)|(「[^「」｣]*?[」｣])|(\([^\(\)]*?\))))(?P<reaction>[ｦ-ﾟ…\.!?ｰ]+)*'
            reg_dic = self.complie_and_get_groupdict_all(reg, text)
            return reg_dic
    def construct_coupled_ma(self, text):
        try:
            ex_str = '[^\(\)\<\>]'
            reg = '\(\(*(?P<label>\<[^\)\(\<\>\|)]+?\>)*(?P<first>[^\)\(\<\>\|)]+)\)*--(?P<second>[^\)\(\<\>\|)]+)*\)'
            reg_group_dic = self.complie_and_get_groupdict(reg, text)
            return reg_group_dic
        except Exception as e:
            p(e)
            return {}
    #[TODO]
    def extract_function(self, text):
            ex_str = '[\w]'
            youbou = '(?P<要望>[!！]|(って|て|で)[!！。]*$|((って|て|で)(ね|よ|てよ|れよ|ほしく|ほしい|ください|[!！。])))'
            order = '(?P<命令>(なさい|れ|せよ|しろ|たまえ))'
            kibou = '(?P<希望>(り|って)*(し|み)*(たい))'
            #
            dantei = '(?P<断定>(の|ん|なん)*(です|でしょ|ます|である|だ|なり|じゃ|や|にゃ))'
            gimon = '(?P<疑問>[?？]|((でしょう|ん|の)*(の|か|かい|かな|かね|かしら|かの)[?？。]*))'
            kanyu = '(?P<勧誘>(しましょう|ませんか|う)[?？。]*)'
            #
            deny = '(?P<否定>(ねえ|ない))'
            ban = '(?P<禁止>(するな|いけない|ねえ))'
            functions = ['(', '|'.join([youbou, order,deny,kibou, kanyu, gimon, dantei,  ban]), ')+']
            reg = ''.join(functions)
            reg_group_dic = self.complie_and_get_groupdict(reg, text)
            # p(reg_group_dic)
            return reg_group_dic
    def convert_time_expression_into_datetime_sec(self, target, target_expression = '秒'):
        if target is None:
            return None
        elif not target.isdigit():
            return None
        elif target_expression in {'秒', 'sec'}:
            sec = int(target)
        elif target_expression in {'分', 'min'}:
            sec = int(target) * 60
        elif target_expression in {'時', 'hour'}:
            sec = int(target) * 3600
        elif target_expression in {'日', 'day'}:
            sec =  int(target) * 3600 * 24
        elif target_expression in {'週', 'week'}:
            sec =  int(target) * 3600 * 24 * 7
        else:
            return None
        return sec
    def extract_modification(self):
            cnt_reg = '\(\<mecab\>\<数\>(?P<count>\d{1,2})(?P<count_scale>度|回)\)(\(\<mecab\>\<副助詞\>(?P<count_preposition>(だけ|ほど|くらい))\))*'
            freq_reg = '\(\<mecab\>\<数\>(?P<frequency>\d{1,2}\w)(?P<frequency_scale>秒|分|時|日|週|sec|min|hour|day|week|year)\).+(?P<frequency_preposition>ごと|おき)\)[にで\s]*'
            duration_reg = '\(\<mecab\>\<数\>(?P<duration>\d{1,2})(?P<duration_scale>秒|分|時|日|週|sec|min|hour|day|week|year)\)[の]*.+(?P<duration_preposition>後まで|間|あいだ|程度|ほど)\)[にで\s]*'
            delay_reg = '\(\<mecab\>\<数\>(?P<delay>\d{1,2})(?P<delay_scale>秒|分|時|日|週|sec|min|hour|day|week|year)\)(?P<delay_preposition>後|すぎ)[にで\s]*'
            # reg = ['.+(' , '|'.join([cnt_reg, duration_reg,  freq_reg, delay_reg]), ')+']
            reg = ''.join(['|'.join([cnt_reg, duration_reg,  freq_reg, delay_reg])])
            reg_group_dic = self.complie_and_get_groupdict(reg, self.text)
def is_kusoripu(self, s):
    if len(s) < 100:
        return False
    if s.count('\u3000') > 5:
        return True
    if s.count('\n') >5:
        return True
    if s.count('\t') >5:
        return True
    emoji_cnt = len(re.findall('[\U0001F0CF-\U000207BF]', s))
    if emoji_cnt > 5:
        return True
    kigou_cnt = len(re.findall('[!-/:-@[-`{-~]', s))
    if kigou_cnt > 20:
        return True
    hankaku_katakana_cnt = len(re.findall('[ｦ-ﾟ]', s))
    if hankaku_katakana_cnt > 7:
        return True
    return False

class MorphologicalAnalysis(MyObject):#MeCab
    def __init__(self):
        self.mecab_place = '/usr/local/bin/mecab'
        self.mecab_dic_place = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
        self.regex_tools = RegexTools()
    def spawn_mecab(self, s):
        try:
            s = s.replace('\n','').replace('(','').replace(')','')
            cmd= 'echo %s | %s -d %s'%(s, self.mecab_place, self.mecab_dic_place)
            p = subprocess.Popen(cmd, shell = True, close_fds = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_data, stderr_data = p.communicate()
            ret = stdout_data
            ret = ret.decode('utf-8')
            ret = ret.replace('\t',',')
            ret = ret.split('\n')
            return ret
        except:
            return ''
    def split_mecab_result(self, info):
        ma = info.split(',')
        length = len(ma)
        if length != 10:
            for x in range(10 - length):
                ma.append('*')
        if ma[7] == '*':
            ma[7] = ma[0]
        return ma
    def integrate_ex_ma(self, cleaned_sentence, ex):
        try:
            if not ex:
                raise
            cl_ls = cleaned_sentence.split('<EX>')
            info_of_words = [self.spawn_mecab(split_sentence) for split_sentence in cl_ls if not split_sentence in {'EOS', ''}]
            ma_ls = [[self.split_mecab_result(info) for info in infox if not info in {'EOS', ''}] for infox in info_of_words]
            special_words_cnt = len(ex)
            if not cl_ls[-1]:
                cl_ls = cl_ls[:-1]
                ma_ls += ['']
            if cl_ls[0]:
                ma_ls = [ma_ls[cursor] + [[ex[cursor], '名詞', '特別', 'regex_special', '*', '*', '*', ex[cursor], '*', '*']] for cursor in range(special_words_cnt)] + [ma_ls[special_words_cnt]]
            else:
                ma_ls = [[[ex[cursor], '名詞', '特別', 'regex_special', '*', '*', '*', ex[cursor], '*', '*']] + ma_ls[cursor] for cursor in range(special_words_cnt)]
            ma_ls = list(chain.from_iterable(ma_ls))
        except:
            infos = self.spawn_mecab(cleaned_sentence)
            ma_ls = [self.split_mecab_result(info) for info in infos if not info in {'EOS', ''}]
        return ma_ls
    def get_mecab_ls(self, s):
        sentence = s
        sentence, ex_ids = self.regex_tools.extract_ids(sentence)
        extracted_rest, ex_ls = self.regex_tools.extract_specific_words(sentence)
        cleaned_sentence, ex_faces = self.regex_tools.extract_kaomojis(extracted_rest)
        ma_ls = self.integrate_ex_ma(cleaned_sentence, ex = ex_ls)
        if ex_ids:
            ma_ls = [ma if not ma[0] == 'atmarkedID' else [ex_ids[0],'名詞', '固有名詞', 'regex_id', '*', '*', '*', ex_ids.pop(0)[1:], '*', '*'] for ma in ma_ls]
        if ex_faces:
            ma_ls = [ma if not ma[0] == '^ ^' else [ex_faces[0], '顔文字', '顔文字', 'regex_顔文字', '*', '*', '*', ex_faces.pop(0), 'カオ', 'カオ'] for ma in ma_ls]
        return ma_ls
    def get_mecab_coupled(self, s, couple_target = {'助詞', '記号', '助動詞'}, cp_kakoi = '({})', cp_splitter = '--', masking_format = '(<{label}>{original})',  is_mask_on = 1):
        def make_none(cursor):
                ma[cursor][0] = None
        def couple_mecab_results(cursor):
            try:
                if cursor < 0:
                    return
                is_joint = False
                ma0 = ma[cursor-1]
                ma1 = ma[cursor]
                ma2 = ma[cursor+1]
                ma11 = ma1[1]
                ma12 = ma1[2]
                ma13 = ma1[3]
                ma01 = ma0[1]
                ma02 = ma0[2]
                ma22 = ma2[2]
                #サ変接続する名詞を接続する。
                if ma[cursor][5] == 'サ変・スル':
                    # if ma02 == 'サ変接続':
                    if ma01 == '名詞':
                        ma[cursor-1][1] = ''
                        is_joint = True
                elif ma[cursor][2] == '接尾':
                        ma[cursor-1][1] = ''
                        is_joint = True
                elif ma02 == '形容動詞語幹':
                    if ma[cursor][1] in {'助詞'}:
                        ma[cursor-1][1] = '形容動詞'
                        ma[cursor][1] = ''
                        is_joint = True
                # elif ma[cursor-1][6] == '連用デ接続':
                #     if ma[cursor][0] == 'で' and ma[cursor][1] == '助詞':
                #         is_joint = True
                #接尾を接続する。
                elif ma12 == '接尾':
                    if is_mask_on:
                        mask_label = None
                        if ma0[3] in {'人名'}:
                            mask_label = ma0[3]
                            is_joint = True
                        if ma0[2] == '数':
                            mask_label = ma0[2]
                            is_joint = True
                        if mask_label:
                            ma[cursor-1][0] = masking_format.format(label = mask_label, original = ma[cursor-1][0])
                # loopで同じ品詞が続く限りjointしていく。
                elif ma11 == ma[cursor+1][1] in couple_target:
                    joint_mas = [ma[cursor]]
                    loop_cursor = cursor + 1
                    while True:
                        try:
                            joint_mas.append(ma[loop_cursor])
                            if ma[cursor][1] == ma[loop_cursor][1]:
                                break
                            loop_cursor += 1
                        except Exception as e:
                            d(e, 'get_mecab_coupled loop')
                            break
                    ma[loop_cursor] = [cp_kakoi.format(cp_splitter.join([joint_ma[k] for joint_ma in joint_mas])) for k in range(10)]
                    ma[loop_cursor][1] = ma11
                    [make_none(erase_cursor) for erase_cursor in range(cursor, loop_cursor)]
                if is_joint:
                    ma[cursor] = [cp_kakoi.format(cp_splitter.join([ma[cursor-1][k], ma[cursor][k]])) for k in range(10)]
                    ma[cursor-1][0] = None
                return ma[cursor]
            except Exception as e:
                d(e, 'mecab couple')
                return None
        ###ここから関数
        if not s:
            return []
        ma = self.get_mecab_ls(s)
        ma+= [[None]*9]*2
        try:
            cp_mas = [cp_ma for cp_ma in [couple_mecab_results(cursor) for cursor in range(len(ma)-1)] if not cp_ma is None and not cp_ma[0] is None]
        except Exception as e:
            cp_mas = {}
        return cp_mas

    #Main
    def get_mecab(self, sentence, mode = 7, form = {'名詞'}, exception = {'記号'}, is_debug = False):
        def is_chosen(w, form, exception):
            if any([w[cursor] in exception for cursor in range(8)]):
                return False
            elif w[0] == '*':
                return False
            elif form is None or w[1] in form:
                return True
            else:
                return False
        try:
            ma = self.get_mecab_ls(sentence)
            if is_debug:
                p('[Debug] mode:')
                p(words)
            return [w[mode] for w in ma if is_chosen(w, form = form, exception = exception)]
        except:
            return ''
    def reverse_mecab_result_into_raw(self, mas):
        ans = '\n'.join(['\t'.join([ma[0], ','.join(ma[1:])]) for ma in mas] + ['EOS'])
        return ans
    def annotate_cp_ma_on_text(self, cp_mas):
        def annotate(ma):
            if ma[1] in {'助詞'}:
                annotate_part = ''.join(['(<mecab>', '<', ma[2],'>', ma[0], ')'])
            elif ma[1] in {'助動詞'}:
                annotate_part = ''.join(['(<mecab>', '<', ma[1],'>', ma[0], ')'])
            elif '--' in ma[0]:
                seqs = ma[0].replace('(', '').replace(')', '').split('--')
                if '>' in ma[0]:
                    # seq = seq[1:-1]
                    annotate_part = ''.join(['(<mecab>']+ seqs+[')'])
                else:
                    annotate_part = ''.join(seqs)
            else:
                annotate_part = ma[0]
            return annotate_part
        ans = ''.join([annotate(ma) for ma in cp_mas])
        return ans

MA = MorphologicalAnalysis()
## ______________________
## CaboChaによる構文解析 //
# import CaboCha
class SyntacticAnalysis(MorphologicalAnalysis):#CaboCha
    def __init__(self):
        self.cabocha_place = '/usr/local/bin/cabocha'
        self.mecab_place = '/usr/local/bin/mecab'
        self.mecab_dic_place = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
    def spawn_cabocha(self, s):
        try:
            cmd= 'echo "{}" | {} -I1 -O4 -f1'.format(s, self.cabocha_place, self.mecab_dic_place)
            p = subprocess.Popen(cmd, shell = True,  close_fds = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            stdout_data, stderr_data = p.communicate()
            ret = stdout_data
            ret = ret.decode('utf-8')
            ret = ret.replace('\t',',')
            ret = ret.split('\n')
            return ret
        except Exception as e:
            d(e, 'spawn_cabocha')
            return ''
    # def get_cabocha_dic(self, mas):
    def get_dics(self, mas, cas):
        dic = {}
        catalog = {}
        cursor = 0
        j = 0
        while not 'EOS' in cas[cursor]:
            if cas[cursor][0] == '*':
                chunk_info = cas[cursor].split(' ')
                # if not chunk_info[1].isdigit():
                chunk_number = int(chunk_info[1])
                content_function_ids_ls = chunk_info[3].split('/')
                content_word_id = int(content_function_ids_ls[0])
                function_word_id = int(content_function_ids_ls[1])
                dic[chunk_number] = {
                    'result' : [],
                    'chunk_id': chunk_number,
                    'reliablity_str': chunk_info[4],
                    'content_word_id': content_word_id,
                    'function_word_id': function_word_id,
                    'chunk_network': { 'id': chunk_number, 'from': [], 'to': []}}
                j = cursor + 1
                dic[chunk_number]['chunk_info'] = chunk_info
                while cas[j][0] != '*':
                    if cas[j] == 'EOS':
                        break
                    else:
                        # MeCab部
                        cama = cas[j].split(',')
                        if cama[7] == '*':
                            cama[7] = cama[0]
                        dic[chunk_number]['result'].append(cama)
                        word_id = mas.index(cama)
                        catalog[word_id] = {}
                        catalog[word_id]['word'] = cama[7]
                        catalog[word_id]['word_id'] = mas.index(cama)
                        catalog[word_id]['chunk_id'] = chunk_number
                        j += 1
            cursor += 1
        return dic, catalog
SyA = SyntacticAnalysis()
class CaboChaClass(MyObject):
    def __init__(self, mas):
        self.mas = mas
        self.mecab = MorphologicalAnalysis()
        self.cabocha = SyntacticAnalysis()
        mas_re = self.mecab.reverse_mecab_result_into_raw(mas)
        cas = self.cabocha.spawn_cabocha(mas_re)
        self.chunk_dic, self.word_catalog = self.cabocha.get_dics(mas, cas)
        [self.get_relation(cainfo) for cainfo in self.chunk_dic.values()]
        self.modify_catalog()
        self.get_pairs()
    def get_relation(self, cainfo):
        number = int(cainfo['chunk_info'][1])
        target_number = int(cainfo['chunk_info'][2][:-1])
        if cainfo['chunk_info'][1] == '0':
            self.chunk_dic[number]['chunk_network']['from'].append('BOS')
        if target_number == -1:
            self.chunk_dic[number]['chunk_network']['to'].append('EOS')
        else:
            self.chunk_dic[number]['chunk_network']['to'].append(target_number)
            self.chunk_dic[target_number]['chunk_network']['from'].append(number)
    def get_pairs(self, pair_type = ''):
        def get_pair(target_word_id, word_data, needs = {'名詞', '形容詞', '動詞', '副詞', '助動詞', '副助詞／並立助詞／終助詞', '記号'}):
            target_chunk_id = word_data['chunk_id']
            _ids = [_id for _id in self.chunk_dic[target_chunk_id]['chunk_network']['to'] if not _id in {'EOS', 'BOS'}]
            if _ids:
                ex_chunks = [(self.chunk_dic[_id]['reliablity_str'], self.chunk_dic[_id]['result'][self.chunk_dic[_id]['content_word_id']][7]) for _id in _ids]
                ex_chunks = sorted(ex_chunks, key = lambda x: x[0], reverse = True)
                ex_chunks_word = [chunk[1] for chunk in ex_chunks]
                self.word_catalog[target_word_id]['pair_content_words'] = ex_chunks_word
                self.word_catalog[target_word_id]['pair_content_ids'] = _ids
            else:
                self.word_catalog[target_word_id]['pair_content_words'] = None
                self.word_catalog[target_word_id]['pair_content_ids'] = None
        [get_pair(target_word_id, catalog_values) for target_word_id, catalog_values in self.word_catalog.items()]
    def modify_catalog(self):
        def mod(word_id, catalog_values):
            chunk_id = catalog_values['chunk_id']
            content_word_id = self.chunk_dic[chunk_id]['content_word_id']
            function_word_id = self.chunk_dic[chunk_id]['function_word_id']
            word = self.word_catalog[word_id]['word']
            self.word_catalog[word_id]['word_type'] = None
            if word != self.chunk_dic[chunk_id]['result'][function_word_id][7]:
                pass
            else:
                self.word_catalog[word_id]['word_type'] = 'function_word'
            if word != self.chunk_dic[chunk_id]['result'][content_word_id][7]:
                pass
            else:
                self.word_catalog[word_id]['word_type'] = 'content_word'
            if '助詞' in self.mas[word_id][1]:
                self.word_catalog[word_id]['word_type'] = 'function_word'
            if self.mas[word_id][1] in {'名詞', '動詞', '形容詞', '形容動詞'}:
                if any([jiritsu in self.mas[word_id][2] for jiritsu in {'自立', '一般', '固有名詞', 'regex-id'}]):
                    self.word_catalog[word_id]['word_type'] = 'content_word'
            if self.mas[word_id][2] == '非自立':
                self.word_catalog[word_id]['word_type'] = 'function_word'
            if not self.word_catalog[word_id]['word_type']:
                self.word_catalog[word_id]['word_type'] = 'function_word'

        def mod2(word_id, catalog_values):
            chunk_id = catalog_values['chunk_id']
            word = self.word_catalog[word_id]['word']
            function_word_id = self.chunk_dic[chunk_id]['function_word_id']
            content_word_id = self.chunk_dic[chunk_id]['content_word_id']
            function_mas = [self.chunk_dic[chunk_id]['result'][function_word_id]]
            pair_function_id = function_word_id - content_word_id + word_id
            try:
                if self.word_catalog[word_id]['word_type'] != 'content_word':
                    pair_function_id = None
                else:
                    if pair_function_id == word_id:
                        pair_function_id = None
                self.word_catalog[word_id]['pair_function_id'] = pair_function_id
                if pair_function_id:
                    self.word_catalog[word_id]['pair_function_words'] = self.word_catalog[pair_function_id]['word']
                else:
                    self.word_catalog[word_id]['pair_function_words'] = None
            except:
                self.word_catalog[word_id]['pair_function_id'] = None
                self.word_catalog[word_id]['pair_function_words'] = None
        [mod(word_id, catalog_values) for word_id, catalog_values in self.word_catalog.items()]
        [mod2(word_id, catalog_values) for word_id, catalog_values in self.word_catalog.items()]
def get_sentence_structure(nlp_dic, begin_id = 'EOS', is_nominalize = False):
    eav_data = {'Entity': '', 'Attribute':'', 'Value':''}
    def grammar_check(info, nlp_dic):
        def extract_eav(elem, nlp_dic = nlp_dic):
            if isinstance(elem, dict):
                newinfo, neweav_data, newnlp_dic = grammar_check(elem, nlp_dic)
                return neweav_data, newnlp_dic
            else:
                return elem, nlp_dic
        username = nlp_dic['username']
        grammar_ls = [key for key, value in info['elems'].items() if value]
        sentence_order = '{S}{ga}{Owo}{wo}{Oni}{ni}{C}{c}{V}{N}'
        #文法間の補正
        if not 'eav' in nlp_dic:
            nlp_dic['eav'] = []
        eav_id = len(nlp_dic['eav'])
        info['grammar'] = grammar_ls
        if not grammar_ls:
            info['is_collapsed'] = True
        else:
            g_set = set(grammar_ls)
            if g_set == {'S', 'V', 'C'}:
                eav_data['Attribute'], nlp_dic = extract_eav(info['elems']['V'])
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
                eav_data['Value'], nlp_dic = extract_eav(info['elems']['C'])
            elif g_set == {'S', 'C'}:
                eav_data['Attribute'] = '__be__'
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
                eav_data['Value'], nlp_dic = extract_eav(info['elems']['C'])
                sentence_order = '{S}{ga}{C}{c}ですね'
            elif g_set == {'S', 'V'}:
                info['Q'] = 'Owo'
                eav_data['Attribute'], nlp_dic = extract_eav(info['elems']['V'])
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
            elif g_set == {'S', 'V', 'Owo'}:
                eav_data['Attribute'], nlp_dic = extract_eav(info['elems']['V'])
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
                eav_data['Value'], nlp_dic = extract_eav(info['elems']['Owo'])
            elif g_set == {'S', 'V', 'Oni'}:
                eav_data['Attribute'], nlp_dic = extract_eav(info['elems']['V'])
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
                eav_data['Value'], nlp_dic = extract_eav(info['elems']['Oni'])
            elif g_set == {'S', 'V', 'Owo', 'Oni'}:
                eav_data['Attribute'], nlp_dic = extract_eav(info['elems']['V'])
                eav_data['Entity'], nlp_dic = extract_eav(info['elems']['S'])
                eav_Owo, eav_ls =  extract_eav(info['elems']['Owo'])
                eav_Oni, eav_ls =  extract_eav(info['elems']['Oni'])
                eav_data['Value'] = {'Attribute':'__to__', 'Entity': eav_Owo, 'Value': eav_Oni}
            else:
                info['is_collapsed'] = True
            if info['phrase_structure'] == 'S':
                if not info['is_nominalize']:
                    info['order'] = sentence_order
            if info['is_negative']:
                try:
                    eav_data['Attribute'] = ''.join(['__not__', eav_data['Attribute']])
                except:
                    eav_data['Attribute'] = '__ERR__'
            return info, eav_data, nlp_dic
    def is_joshi(ma, joshis = {'は', 'って', 'も', 'が'}):
        if '助詞' in ma[1]:
            if ma[0] in joshis:
                return True
            if 'CP' in ma[2]:
                return any([joshi in ma[0] for joshi in joshis])
        return False
    def get_from_id(target_chunk):
        from_id_ls = target_chunk['chunk_network']['from']
        if from_id_ls:
            return from_id_ls[-1]
        else:
            return None
    def is_negative_chunk(target_chunk, not_jvs = {'ない', 'ぬ'}):
            target_jvs = [ma[7] for ma in target_chunk['result'] if ma[1] in {'助動詞'}]
            if any([not_jv in target_jvs for not_jv in not_jvs]):
                return True
            else:
                return False
    def check_rest_words(word, nlp_dic, add = []):
        if word in nlp_dic['rest']:
            nlp_dic['rest'].remove(word)
            if add:
                word = ''.join([word + ''.join(add)])
            return word, nlp_dic
        else:
            return '', nlp_dic
    def get_modification(target_chunk, target_ma, nlp_dic):
        first_result = target_ma[7]
        if not '名詞' in target_ma[1]:
            result, nlp_dic = check_rest_words(first_result, nlp_dic)
            return result, nlp_dic
        if not first_result:
            return '', nlp_dic
        _C = ''
        is_negative = False
        sentence_order = '{C}{N}{S}'
        relation = ''
        result_list = []
        tsunagi = ''
        if first_result in {'こと', 'の'}:
            first_result, nlp_dic = check_rest_words(first_result, nlp_dic)
            if first_result:
                return get_sentence_structure(nlp_dic, begin_id = target_chunk['chunk_network']['id'], is_nominalize = True)
        target_chunk_mas = target_chunk['result']

        try:
            result_index = all_mas.index(target_ma)
        except Exception as e:
            result_index = 0
        _index = result_index
        while _index > 0:
            _index -= 1
            result_before_ma = all_mas[_index]
            if result_before_ma[1] in {'名詞', '固有名詞', '接頭詞'}:
                before_word, nlp_dic = check_rest_words(result_before_ma[7], nlp_dic)
                if before_word:
                    result_list.insert(0, before_word)
            else:
                break
        if result_list:
            result_list.append(first_result)
            from_chunks_mods = []
        else:
            result_list = [first_result]
            from_chunks_mods = [chunks[_id] for _id in target_chunk['chunk_network']['from'] if not _id in {'BOS', 'EOS'}]
        if from_chunks_mods:
            #並列化
            mod_chunks = [chunk for chunk in from_chunks_mods if any([ma[0] in {'と'} and ma[2] in {'並立助詞', '格助詞'} for ma in chunk['result']])]
            if mod_chunks:
                mod_mas = mod_chunks[-1]['result']
                heiretsu_words = [ma for ma in mod_mas if '名詞' in ma[1]]
                try:
                    heiretsu_word, nlp_dic = check_rest_words(heiretsu_words[-1][7], nlp_dic)
                    result_list += heiretsu_word
                    tsunagi = '<&>'
                except Exception as e:
                    # p(e)
                    pass
            else:
                #連体化
                mod_chunks = [chunk for chunk in from_chunks_mods if any([(ma[0] in {'の'} and ma[2] == '連体化') or ma[6] == '体言接続' for ma in chunk['result']])]
            if mod_chunks:
                mod_mas = mod_chunks[-1]['result']
                mod_words = [ma[7] for ma in mod_mas if '名詞' in ma[1]]
                sentence_order = '{C}{N}の{S}'
                relation = '__of__'
            else:
                mod_chunks = [chunk for chunk in from_chunks_mods if any([ma[1] == '動詞' for ma in chunk['result']])]
            if mod_chunks:
                mod_mas = mod_chunks[-1]['result']
                mod_words = [ma[7] for ma in mod_mas if ma[1] in {'動詞'}]
                relation = '__which__'
                sentence_order = '{C}{N}{S}'
            else:
                mod_mas = from_chunks_mods[-1]['result']
                mod_words = [ma[7] for ma in mod_mas if ma[1] in {'形容詞'}]
                sentence_order = '{C}{N}{S}'
                relation = '__be__'
            # p(mod_words)
            if mod_words:
                _C, nlp_dic = check_rest_words(mod_words[-1], nlp_dic)
                if _C:
                    is_negative = is_negative_chunk(from_chunks_mods[-1], not_jvs = {'ない', 'ぬ'})
        result = tsunagi.join(result_list)
        if result == first_result:
            result, nlp_dic = check_rest_words(result, nlp_dic)
            if _C:
                info = {'elems': {
                            'S':result,
                            'V': relation,
                            'Owo': '',
                            'Oni': '',
                            'C': _C,
                        }, 'Q':'', 'is_nominalize': False,'is_negative': is_negative, 'is_collapsed': False, 'order': sentence_order, 'phrase_structure': 'NP'}
                result, eav_data, nlp_dic = grammar_check(info, nlp_dic)
        return result, nlp_dic

    gimongo_dic = {
        '何': 'what',
        'なに': 'what',
        'どこ':'where',
        '誰':'who',
        'なぜ': 'why',
        'なんで': 'why',
        '何で': 'why',
        'どうして': 'why',
        'いつ': 'when',
        'だれ': 'who',
        'どうやって':'how'
    }
    _S =  ''
    _V = ''
    _Owo = ''
    _Oni = ''
    _C = ''
    _Q = ''
    is_negative = False
    is_collapsed = False
    is_V = False
    # CHUNKsの抽出
    chunks = nlp_dic['SyA_chunk']
    all_chunks = chunks.values()
    all_chunks_len = len(all_chunks)
    all_mas_nested = [chunk['result'] for chunk in all_chunks]
    all_mas = [e for inner_list in all_mas_nested for e in inner_list]
    # 述語CHUNKの抽出
    s1v_chunks = []
    while not s1v_chunks:
        s1v_chunks = [chunk for chunk in all_chunks if begin_id in chunk['chunk_network']['to'] and any([ma[1] in {'名詞', '固有名詞', '形容詞', '動詞'} for ma in chunk['result']])]
        if not begin_id in {'BOS', 'EOS'}:
            if int(begin_id) < 0:
                is_collapsed = True
                return {}, nlp_dic
            begin_id -= 1
        else:
            begin_id = all_chunks_len-1
    s1v_chunk = s1v_chunks[-1]
    s1v_mas = s1v_chunk['result']
    #疑問語の検出
    Qadv_chunks = [ls for ls in [[ma[0] for ma in all_chunk['result'] if ma[1] in {'副詞', '名詞'} and ma[0] in gimongo_dic] for all_chunk in all_chunks] if ls]
    if Qadv_chunks:
        Q_original, nlp_dic = check_rest_words(Qadv_chunks[0][0], nlp_dic)
        if Q_original:
            _Q = gimongo_dic[Q_original]
    if any([ma[0] in {'?', '？'} for ma in s1v_mas]):
        _Q = '__if__'
    #否定語の検出
    is_negative = is_negative_chunk(target_chunk = s1v_chunk, not_jvs = {'ない', 'ぬ'})
    #述語動詞の検出
    v_mas = [ma for ma in s1v_mas if ma[1] in {'動詞'} and not ma[2] in {'非自立'}]
    if v_mas:
        v_ma = v_mas[-1]
        #'サ変・スル'のチェック
        if v_ma[5] != 'サ変・スル':
            _V, nlp_dic = check_rest_words(v_ma[7], nlp_dic)
        else:
            v_ma_index = s1v_mas.index(v_ma)
            v_ma_before = s1v_mas[v_ma_index-1]
            if v_ma_before[1] == '名詞':
                _V, nlp_dic = check_rest_words(v_ma_before[7], nlp_dic, add = ['する'])
            elif '助詞' in v_ma_before[1] and v_ma_before[0] in {'を'}:
                v_ma_before2 = s1v_mas[v_ma_index-2]
                if v_ma_before2[1] == '名詞':
                    _V, nlp_dic = check_rest_words(v_ma_before[7], nlp_dic, add = ['する'])
                    _V, nlp_dic = check_rest_words(v_ma_before2[7], nlp_dic, add = [_V])
            else:
                from_id = get_from_id(target_chunk = s1v_chunk)
                if not from_id in {None, 'BOS', 'EOS'}:
                    v_ma2 = chunks[from_id]['result']
                    v_sanoun = [ma[7] for ma in v_ma2 if ma[1] == '名詞' and ma[2] == 'サ変接続']
                    if v_sanoun:
                        _V, nlp_dic = check_rest_words(v_sanoun[0], nlp_dic, add = ['する'])
    #FROM_CHUNKS
    from_chunk_ids = s1v_chunk['chunk_network']['from']
    if not from_chunk_ids:
        is_collapsed = True
        return { 'elems': {
            'S':_S,
            'V': _V,
            'Owo': _Owo,
            'Oni': _Oni,
            'C':_C,
        }, 'Q':_Q, 'is_negative':is_negative, 'is_collapsed': is_collapsed, 'order': '', 'is_nominalize': is_nominalize, 'phrase_structure': ''}
    from_chunks = [chunks[_id] for _id in set(from_chunk_ids) if not _id in {'EOS', 'BOS'}]
    #主語の検出
    s_chunks = [ls for ls in [[from_chunk for ma in from_chunk['result'] if is_joshi(ma, joshis = {'は', 'って', 'も', 'が'})] for from_chunk in from_chunks] if ls]
    if not s_chunks:
        if any([is_joshi(ma, joshis = {'は', 'って', 'も', 'が'}) for ma in chunks[s1v_chunk['chunk_network']['id']]['result']]):
            s_chunks = [[s1v_chunk]]
    if s_chunks:
        #s_chunk = s_chunks[-1][0] だと、述語からもっとも離れたものが主語になる。公文書的
        s_chunk = s_chunks[0][0]
        s_mas = [ma for ma in s_chunk['result'] if ma[1] in {'名詞', '固有名詞'}]
        if s_mas:
            _S, nlp_dic = get_modification(target_chunk = s_chunk, target_ma = s_mas[0], nlp_dic = nlp_dic)
    #述語補語の検出
    if not v_mas:
        c_mas = [ma for ma in s1v_mas if ma[1] in {'名詞', '固有名詞', '形容詞', '接頭詞'} and ma[2] != '非自立']
        if c_mas:
            _C, nlp_dic = get_modification(target_chunk = s1v_chunk, target_ma = c_mas[-1], nlp_dic = nlp_dic)
    # 目的語ヲの検出
    Owo_chunks = [ls for ls in [[from_chunk for ma in from_chunk['result'] if '助詞' in ma[1] and ma[0] in {'を'}] for from_chunk in from_chunks] if ls]
    if not Owo_chunks:
        Owo_chunks = [ls for ls in [[all_chunk for ma in all_chunk['result'] if '助詞' in ma[1] and ma[0] in {'を'}] for all_chunk in all_chunks] if ls]
    if Owo_chunks:
        Owo_chunk = Owo_chunks[-1][-1]
        Owo_mas = [ma for ma in Owo_chunk['result'] if ma[1] in {'名詞', '固有名詞'}]
        if Owo_mas:
            # S内の第二層の主述関係 S2
            _Owo, nlp_dic = get_modification(target_chunk = Owo_chunk, target_ma = Owo_mas[-1], nlp_dic = nlp_dic)
    # 目的語ニの検出
    Oni_chunks = [ls for ls in [[from_chunk for ma in from_chunk['result'] if '助詞' in ma[1] and ma[0] in {'に', 'にとって', 'には'}] for from_chunk in from_chunks] if ls]
    if not Oni_chunks:
        Oni_chunks = [ls for ls in [[all_chunk for ma in all_chunk['result'] if '助詞' in ma[1] and ma[0] in {'に', 'にとって', 'には'}] for all_chunk in all_chunks] if ls]
    if Oni_chunks:
        Oni_chunk = Oni_chunks[-1][-1]
        Oni_mas = [ma for ma in Oni_chunk['result'] if ma[1] in {'名詞', '固有名詞'}]
        if Oni_mas:
            # S内の第二層の主述関係 S2
            _Oni, nlp_dic = get_modification(target_chunk = Oni_chunk, target_ma = Oni_mas[-1], nlp_dic = nlp_dic)
    info = {
        'elems': {
            'S':_S,
            'V': _V,
            'Owo': _Owo,
            'Oni': _Oni,
            'C':_C,
        },'Q':_Q, 'is_negative': is_negative, 'is_collapsed': is_collapsed, 'order': '{S}{ga}{Owo}{wo}{Oni}{ni}{C}{c}{V}{N}', 'is_nominalize': is_nominalize, 'phrase_structure': 'S'}
    try:
        info, eav_data, nlp_dic = grammar_check(info, nlp_dic)
    except:
        pass
    if not 'eav' in nlp_dic:
        nlp_dic['eav'] = []
    if not eav_data in nlp_dic['eav']:
        nlp_dic['eav'].append(eav_data)
    if not 'is_collapsed' in info:
            info['is_collapsed'] = False
    return info, nlp_dic
def anal_info(info, nominalize_list = ['こと', 'の', 'なんてこと', 'ということ']):
    import numpy as np
    def anal_elem(elems, target, joshis = ['が']):
        try:
            elem = elems[target]
            if isinstance(elem, dict):
                elem_ans = anal_info(elem)
                joshi = np.random.choice(joshis)
                if elem['is_nominalize']:
                    if elem_ans[-1] in {'の', 'ん'} and elem_ans[-2] == 'い':
                        elem_ans = elem_ans[:-1]
                    nominalize = np.random.choice(nominalize_list)
                    joshi = ''.join([nominalize, joshi])
            elif not elem:
                if elem == '__of__':
                    elem_ans = ''
                    joshi = ''
                elif elem == '__be__':
                    elem_ans = 'である'
                else:
                    elem_ans = elem
                joshi = np.random.choice(joshis)
                if '<no>' in elem_ans:
                    elem_ans = elem_ans.replace('<no>', 'の')
                # Cが形容詞なら...
                if target == 'C':
                    if elem_ans[-1]  in {'い'}:
                        joshi = joshi[-1]
            else:
                elem_ans = ''
                joshi = ''
            return elem_ans, joshi
        except Exception as e:
            return '', ''
    #
    ans = ''
    sentence_order = info['order']

    ansS, ansS_joshi = anal_elem(info['elems'], 'S', ['が'])
    ansOwo, ansOwo_joshi = anal_elem(info['elems'], 'Owo', ['を'])
    ansOni, ansOni_joshi = anal_elem(info['elems'], 'Oni', ['に'])
    ansC, ansC_joshi = anal_elem(info['elems'], 'C', ['なの', 'なん'])
    ansV, ansV_joshi = anal_elem(info['elems'], 'V')
    #否定
    if info['is_negative']:
        ansN = 'ことはない'
    else:
        ansN = ''
    infoQ = info['Q']
    if info['phrase_structure'] != 'S':
        if info['is_nominalize']:
            sentence_order = info['order']
    #     #疑問部
    elif infoQ == '__if__':
        sentence_order =  ''.join(['はい、', sentence_order])
    #文章生成部
    ans = sentence_order.format(S = ansS, ga = ansS_joshi, Owo = ansOwo, wo = ansOwo_joshi, Oni = ansOni, ni= ansOni_joshi, C = ansC, c = ansC_joshi, V = ansV, N = ansN, filler = 'えっと', YOU = '{username}')
    if '、' in ans:
        splitKuten = ans.split('、')
        ans = ''.join([splitKuten[0], '、', ''.join(splitKuten[1:])])
    ans = ans.replace('<&>', 'と')
    return ans
class RegexClass(RegexTools):
    def __init__(self, s):
        self.text = s
        self.rest_text = ''
        self.Dativ = None
        self.Nominativ = None
        self.Akkusativ = None
        mod_dic = self.extract_modification()
        if mod_dic:
            self.cnt = mod_dic['cnt']
            self.delay_sec = self.convert_time_expression_into_datetime_sec(target = mod_dic['delay'], target_expression = mod_dic['delay_scale'])
            self.duration_sec = self.convert_time_expression_into_datetime_sec(target = mod_dic['duration'], target_expression = mod_dic['duration_scale'])
            self.frequency_sec = self.convert_time_expression_into_datetime_sec(target = mod_dic['frequency'], target_expression = mod_dic['frequency_scale'])
        else:
            self.delay_sec = None
            self.duration_sec = None
            self.frequency_sec = None
            self.cnt = None
    def main(self):
        # if '(' in self.text and ')' in self.text:
        #     return self.extract_cmds_dic(self.text)
        # else:
        if True:
            try:
                reg_dic = self.nlp_regex()
                cmd_dic = {}
                if not reg_dic:
                    return {}
                if not self.Dativ is None:
                    if 'と' in self.Dativ:
                        split_Dativ = self.Dativ.split('と')
                        self.target = split_Dativ[0].replace('@', '')
                        self.target1 = split_Dativ[1].replace('@', '')
                        try:
                            self.target2 = split_Dativ[2].replace('@', '')
                        except:
                            pass
                    else:
                        self.target = self.Dativ
            except Exception as e:
                p(e)
                reg_dic = {}
            return reg_dic
    def nlp_regex(self):
        try:
            ex_str = '[^がをにはで\(\)\<\>\s]'
            def heiretsuka(label = 'Dativ'):
                return ['(?P<', label, '>', ex_str, '+?)', '(\(\<mecab\>\<並立助詞\>.+?\)(?P<', label, '2>', ex_str, '+?))*', '(\(\<mecab\>\<並立助詞\>.+?\)(?P<', label, '3>.+?))*']
            shugo_reg = ['('] + heiretsuka(label = 'Nominativ') + ['\(\<mecab\>\<係助詞\>[はが]\)[、,\s]*)*']
            akkusativ_reg = ['('] + heiretsuka(label = 'Dativ') + ['\(\<mecab\>\<格助詞\>[にへ]\)[、,\s]*)*']
            dativ_reg = ['((?P<Akkusativ>', ex_str, '+?)\s*\(\<mecab\>\<格助詞\>[を]\)[、,\s]*)*']
            mokuteki_reg = akkusativ_reg + dativ_reg
            # mokuteki_reg = ''.join(['(?P<Dativ>', '\(.+?\))'])
            modification_reg = []
            # .*(で|ろ|れ|せ|な|たい|れよ|！|!))(いで|よ|って|ほしい|ください|)
            action = ['(?P<action>', ex_str, '+?)(?P<action_>(\(\<mecab\>接続助詞:[て]\)|なさい|てよ|れよ))']
            reg = ''.join(['\s*'] + shugo_reg + mokuteki_reg + modification_reg + action)
            # reg = mokuteki_reg
            reg_group_dic = self.complie_and_get_groupdict(reg, self.text)
            return reg_group_dic
        except Exception as e:
            p(e)
            return {}
##
#
#
#
#
#
#
class NLPdatas(MyObject):
    def __init__(self, sentence):
        self.original_text = sentence
        if not '。' in self.original_text:
            self.split_texts = [self.original_text]
        else:
            self.split_texts = self.original_text.split('。')
        self.summaries = {text_number: NLPdata(self.split_texts[text_number]) for text_number in range(len(self.split_texts))}
        functions = [nlp_data for nlp_data in self.summaries.values() if not nlp_data.summary.function in {'?', '', None}]
        if functions:
            self.main = functions[-1]
        else:
            self.main = [summary for summary in self.summaries.values()][-1]
class NLPSummary(MyObject):
    def __init__(self):
        self.text = None
        self.entity = ''
        self.dativ = ''
        self.akkusativ = ''
        self.value = ''
        self.function = ''
    def has_function(self, *args):
        if self.function is None:
            return False
        else:
            return any(arg in self.function for arg in args)

class NLPdata(MyObject):
    def __init__(self, sentence):
        # super().__init__(sentence)
        self.text = sentence
        self.summary = NLPSummary()
        self.summary.text = self.text
        # ##MorphologicalAnalysis
        self.MA = MorphologicalAnalysis()
        self.mas = self.MA.get_mecab_ls(self.text)
        self.coupled_mas = self.MA.get_mecab_coupled(self.text, couple_target = {'助詞', '記号', '助動詞', '名詞'}, cp_kakoi = '({})', cp_splitter = '--', masking_format = '(<{label}>{original})',  is_mask_on = 1)
        self.annotated_text = self.MA.annotate_cp_ma_on_text(self.coupled_mas)
        ##Regular Expression
        self.regex_class = RegexClass(self.annotated_text)
        # ##SyntacticAnalysis
        self.joint_mas = self.MA.get_mecab_coupled(self.text, couple_target = {'記号', '助動詞', '名詞'}, cp_kakoi = '{}', cp_splitter = '', masking_format = '{original}',  is_mask_on = 1)
        self.ma_len = len(self.joint_mas)
        self.cabocha_class = CaboChaClass(self.joint_mas)
        self.value_function_ids = []
        self.value_function_mas = []
        self.value_ma = []
        try:
            value_info = [(info, info['word_id'], info['pair_function_id']) for key, info in self.cabocha_class.word_catalog.items() if info['word_type'] != 'function_word']
            if value_info:
                info, self.value_id, value_function_id = value_info[-1]
                if value_function_id is None:
                    value_function_id = self.value_id + 1
                self.value_ma = self.joint_mas[self.value_id]
                self.summary.value = self.value_ma[7]
                if value_function_id in self.cabocha_class.word_catalog:
                    while self.cabocha_class.word_catalog[value_function_id]['word_type'] == 'function_word':
                        value_function_id += 1
                        if value_function_id +2 > self.ma_len:
                            break
                if value_function_id +1 > self.ma_len:
                    value_function_id = self.ma_len -1
                if value_function_id:
                    self.value_function_id_range = range(self.value_id + 1, value_function_id + 1)
                    self.value_function_mas = [self.joint_mas[function_id] for function_id in self.value_function_id_range]
        except Exception as e:
            d(e, 'NLPdata.init.ma')
            pass
        else:
            self.summary.function = self.judge_function()
            # p(self.summary.function )
        try:
            cabocha_akkusativ = self.extract_phrase_with_joshi({'を', 'で'})
            if cabocha_akkusativ:
                self.summary.akkusativ = cabocha_akkusativ[0]
        except Exception as e:
            d(e, 'NLPdata.init.ak')
            pass
        try:
            cabocha_dativ = self.extract_phrase_with_joshi({'に', 'へ'})
            if cabocha_dativ:
                self.summary.dativ = cabocha_dativ[0]
        except Exception as e:
            d(e, 'NLPdata.init.da')
            pass
        try:
            cabocha_entity = self.extract_phrase_with_joshi({'が', 'は', 'とは'})
            if cabocha_entity:
                self.summary.entity = cabocha_entity[0]
        except Exception as e:
            d(e, 'NLPdata.init.en')
            pass
    def judge_function(self):
        if not self.value_ma:
            return None
        elif not self.value_function_mas:
            if '命令' in self.value_ma[6]:
                return '命令'
            else:
                return None
        func_text = ''.join([ma[0] for ma in self.value_function_mas])
        function_name = ''
        reg_dic = self.regex_class.extract_function(func_text)
        function_names = [function_name for function_name, extracted in reg_dic.items() if not extracted is None]
        if function_names:
            p(function_names)
            if '断定' in function_names:
                function_names.remove('断定')
            if '否定' in function_names:
                function_name = ''.join(['否定', '(', function_name, ')'])
                function_names.remove('否定')
            if '疑問' in function_names:
                function_name = ''.join(['疑問', '(', function_name, ')'])
                function_names.remove('疑問')
            if function_names:
                if function_name != '':
                    function_name = ''.join(['疑問', '(', function_names[0], ')'])
                else:
                    function_name = function_names[0]
        if function_name == '断定':
            if '命令' in self.value_ma[6]:
                function_name = '命令'
        return function_name
    def extract_phrase_with_joshi(self, joshi_set = {'に', 'へ'}):
        word_catalog_items = self.cabocha_class.word_catalog.items()
        try:
            if self.value_ma:
                words = [value['word'] for key, value in word_catalog_items if value['pair_function_words'] in joshi_set and self.value_ma[7] in value['pair_content_words']]
            else:
                raise Exception
        except:
            words = []
        if not words:
            words = [value['word'] for key, value in word_catalog_items if value['pair_function_words'] in joshi_set]
        if not words:
            words = []
        return words
    def extract_action_reg(self, reg_dic):
        ex_actions = [cp_ma[7] for cp_ma in self.coupled_mas_dic if cp_ma[0] in self.action and cp_ma[1] in {'動詞'} and cp_ma[2] in {'自立'}]
        if not ex_actions:
            ex_action = ''
        else:
            ex_action = ex_actions[-1]
        return ex_action
    def convert_coupled_mas_easy(self):
        def construct_dic_into_text(cp_ma, k):
            dic = self.regex_class.construct_coupled_ma(cp_ma[k])
            if k in {0, 7}:
                if not dic['label'] is None:
                    ans = ''.join([dic['label'], dic['second']])
                else:
                    ans = ''.join([dic['first'], dic['second']])
            elif k in {8,9}:
                ans = ''.join([dic['first'], dic['second']])
            elif dic['second'] != '*':
                ans = ''.join(['CP2:', dic['second']])
            elif dic['first'] != '*':
                ans = ''.join(['CP1:', dic['first']])
            else:
                ans = '*'
            return ans
        return [[construct_dic_into_text(cp_ma, k) if '(' in cp_ma[k] else cp_ma[k] for k in range(len(cp_ma))] for cp_ma in self.coupled_mas]
class Temp(MyObject):
    pass
if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    text = '''海未（この待ち時間、というのも風俗の醍醐味の一つではありますね。）   '''    # text = 'したい'
    # a = MA.get_mecab(text, mode = 7, form = {'名詞', '動詞', '形容詞'}, exception = {'記号'}, is_debug = False)
    # p(np.random.choice(a))
    # reg = RegexTools()
    # p(reg.extract_discorse(text))
    text = 'a'
    p(text[:3])
    # aa = ['a', tmp, 'b', 'a', 'c', 'd', 'e']
    # import random
    # p(random.sample(aa, 3))
    # p(MA.get_mecab_ls(text))
    # p(MA.get_mecab_coupled(text))
    # # p(NLPdata(text).regex_analysis.__dict__)
    # nlp_data = NLPdatas(text).main
    # p(nlp_data.summary)
    # p(nlp_data.summary.has_function('希望', '要望', '勧誘'))
    # p(nlp_data.summary.has_function('疑問'))
    # ans = operate_sql.get_phrase(status =  'yes', character = character)
    # p(ans)

