#!/usr/bin/env python
# -*- coding: utf-8 -*-
import natural_language_processing
from sql_models import *
import _
from _ import p, d, MyObject, MyException
import operate_sql

# from sklearn.cluster import KMeans
# def kmeans(features, k=10):
#     km = KMeans(n_clusters=k, init='k-means++', n_init=1, verbose=True)
#     km.fit(features)
#     return km.labels_
# def plot(features, labels):
#     import matplotlib.pyplot as plt
#     plt.scatter(features[:, 0], features[:, 1], c=labels, cmap=plt.cm.jet)
#     plt.show()

# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.cluster import KMeans
# from sklearn.decomposition import TruncatedSVD
# from sklearn.preprocessing import Normalizer
# def main(items, isPlot =False):
#     vectorizer = TfidfVectorizer(
#         use_idf=True
#     )
#     X = vectorizer.fit_transform(items)
#     lsa = TruncatedSVD(10)
#     X = lsa.fit_transform(X)
#     X = Normalizer(copy=False).fit_transform(X)
#     km = KMeans(init='k-means++',)
#     km.fit(X)
#     kmlabel = km.labels_
#     print(kmlabel)
#     labeled_items = [(kmlabel[i], items[i]) for i in range(len(kmlabel))]
#     labelcnt = len(kmlabel)
#     i =0
#     while(True):
#       print('++++++++++++++++++')
#       print('クラスタNo.', i)
#       [print('・', item[1]) for item in labeled_items if item[0] == i]
#       i += 1
#       if i > labelcnt:
#         break
#     if isPlot:
#       plot(X, km.labels_)
def extract_haiku(mas):
    mas = [ma for ma in mas if not ma[1] in {'記号', '顔文字'}]
    yomi = [ma[9] for ma in mas]
    if '*' in yomi:
        return ''
    else:
        origin = [ma[0] for ma in mas]
        metaS = [ma[1] for ma in mas]
        yomi = [y.replace('ー', '').replace('ャ', '').replace('ュ', '').replace('ョ', '') for y in yomi]
    wlens = [len(w) for w in yomi]
    word_total_len = np.sum(wlens)
    if not word_total_len in {17, 18}:
        return ''
    else:
        wlenArr = [np.sum(wlens[0:i+1]) for i in range(len(wlens))]
        if 5 in wlenArr and 12 in wlenArr and 17 in wlenArr:
            index1 = wlenArr.index(5)+1
            index2 = wlenArr.index(12)+1
            comment =  '[5-7-5]'
        elif 5 in wlenArr and 13 in wlenArr and 18 in wlenArr:
            index1 = wlenArr.index(5)+1
            index2 = wlenArr.index(13)+1
            comment = '[5-8-5]'
        else:
            return ''
        ExSets = {'助詞', '助動詞', '記号'}
        if mas[index1][1] in ExSets or mas[index2][1] in ExSets:
            return ''
        ExSets2 = {'非自立', '接尾'}
        if mas[index1][2] in ExSets2 or mas[index2][2] in ExSets2:
            return ''
        return ''.join(['\n',''.join(origin[0:index1]), '\n    ', ''.join(origin[index1:index2]), '\n        ', ''.join(origin[index2:]), '...', comment])

def getBoomWords(username = '_umiA', n = 400):
    try:
        with twlog_sql.transaction():
            tweets = Tweets.select().where((operateTweets.screen_name == username) & (~Tweets.text.contains('RT'))).order_by(Tweets.createdat.desc()).limit(n)
            tweetslist = [clean_text(tweet.text) for tweet in tweets]#  if 'RT' not in tweet.text]
            # print([tweet.text for tweet in tweets])
            tweetslist = [Kaomoji(tweet) for tweet in tweetslist]
            nouns = [natural_language_processing.MA.get_mecab(s[0], form='名詞', exception="数,接尾,非自立,接続助詞,格助詞,代名詞",returnstyle = 'list',Debug=0) for s in tweetslist]
            # nounslist = list(set(chain.from_iterable(nouns)))
            nounslist = list(chain.from_iterable(nouns))
            # print(nounslist)
            noun2list = [noun for noun in nounslist if len(noun) > 2]
            # # print(noun2list)
            # randn = random.choice(noun2list)
            if noun2list == []:
                print(user + 'さんのデータが足りません。もう少し経ってから再試行してみてください。')
            else:
                print(user + 'さんが最近よくつかう言葉は...')
                counter = Counter(noun2list)
                for word, cnt in counter.most_common(5):
                    print('☆ ', word)
                print('です。')
    except IntegrityError as ex:
        print(ex)
        db.rollback()    


class TFIDF():
  def __init__(self, option = ''):
    self.option = option
  def increase_document_frequency(self, word):
    try:
      # talk_sql.create_tables([managementInfos, tf_idf], True)
      with talk_sql.transaction():
        try:
          wdb, created = TFIDFModel.get_or_create(word = word)
          if not created:
            try:
              wdb.df +=  1
            except:
              wdb.df = 1
            wdb.save()
        except Exception as e:
          print('')
        talk_sql.commit()
    except Exception as e:
      talk_sql.rollback()
      # print(e)
  
  def upsert_word(self, ma, is_learn = False):
    genkei = ma[7]
    hinshi = ma[1]
    hinshi2 = ma[2]
    document_frequency = 1;
    is_created = False
    try:
      # talk_sql.create_tables([managementInfos, tf_idf], True)
      with talk_sql.transaction():
        try:
          wdb, is_created = TFIDFModel.get_or_create(word = genkei, hinshi = hinshi, hinshi2 = hinshi2)
          if not is_learn:
            document_frequency = 1
          elif is_created:
            wdb.word = genkei
            wdb.yomi = ma[8]
            wdb.hinshi = ma[1]
            wdb.hinshi2  = ma[2]
            wdb.info3  = ma[3]
            wdb.termcnt = 1
            wdb.df = 1
            wdb.term_frequency = 1
            wdb.save()
            document_frequency = 1
          else:
            try:
              wdb.df +=  1
            except:
              wdb.df = 1
            wdb.save()
            document_frequency = wdb.df
        except Exception as e:
          print('')
        talk_sql.commit()
    except Exception as e:
      talk_sql.rollback()
      # print(e)
    return document_frequency, is_created
  
  def calc_tf_idf(self, w, term_frequency_dic, cnt = 5, total_documents = 30000, is_debug = False):
    word = w[7]
    word_cnt = term_frequency_dic[word]
    term_frequency =  word_cnt / cnt
    if word == '*':
      return ''
    else:
      document_frequency, is_created = self.upsert_word(w)
    try:
      base_inversed_document_frequency = total_documents / document_frequency
      inversed_document_frequency = 1 + np.log2(base_inversed_document_frequency)
    except:
      inversed_document_frequency = 1
    tf_idf = term_frequency * inversed_document_frequency
    w.append(tf_idf)
    w.append(is_created)
    if is_debug:
      print(word, str(round(tf_idf, 2)))
    return w
  
  def append_tf_idf_on_ma_result(self, ma, total_documents = 420000, is_learn = False, is_debug = False):
    # ma = natural_language_processing.MA.get_mecab_coupled(s)
    word_cnt = len(ma)
    word_ls = [w[7] for w in ma]
    counter = Counter(word_ls)
    term_frequency_dic = {}
    for word, cnt in counter.most_common():
      term_frequency_dic[word] = cnt
    result = [self.calc_tf_idf(w, term_frequency_dic, cnt = 5, total_documents = total_documents, is_debug = is_debug) for w in ma]
    if is_learn:
      for key in term_frequency_dic.keys():
        self.increase_document_frequency(key)
    return result

  def learn_tf_idf(self, sList):
    # result = [Main(s, 1, True, True) for s in sList]
    # print(len(result))
    i = 1;
    for s in sList:
      print('++++++++++++++++++++++++++++++++++++++++++++++++++')
      print(i, s)
      try:
        ma = natural_language_processing.MA.get_mecab_coupled(s)
        mas = self.append_tf_idf_on_ma_result(ma, i, True, True)
      except Exception as e:
        print('')
      i += 1  
  def extract_tf_idf(self, ma, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exception = {'数'}):
    def is_keyword(x, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exceptions = {'数'}):
      try:
        if x[1] in needs:
          if not x[2] in exceptions:
            return True
        elif x[2] in needs:
          if not x[2] in exceptions:
            return True
        return False
      except Exception as e:
        return False
    def sort_tf_idf_ma(tf_idf_ma, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, exceptions = {'数'}):
      return [x for x in sorted(tf_idf_ma, key = lambda x: x[10], reverse = True) if is_keyword(x, needs, exceptions)]
    ##
    tf_idf_ma = self.append_tf_idf_on_ma_result(ma, total_documents = 420000, is_learn = False, is_debug = False)
    result = sort_tf_idf_ma(tf_idf_ma, needs)
    return result
  
  def calc_keywords_tf_idf(self, ma, length = 1, needs = {'名詞', '固有名詞', '動詞', '形容詞'}):
    extracted_keywords_ma = self.extract_tf_idf(ma, needs)
    seen = set()
    seen_add = seen.add
    keywords = [(x[7], x[1], x[10], x[11]) for x in extracted_keywords_ma if len(x[0])>length]
    keyword_tf_idf = np.array([x for x in keywords if x[0] not in seen and not seen_add(x[0])])
    return keyword_tf_idf
  
  def get_random_keywords(self, keywords, random_cnt = 1):
    kwcnt = len(keywords)
    tf_idf = np.array([float(x[2]) for x in keywords])
    per = np.sum(tf_idf)
    p = tf_idf / per
    if random_cnt > kwcnt:
      random_cnt = kwcnt
    try:
      return np.random.choice([x[0] for x in keywords], random_cnt, replace=False, p = p)
    except:
      return ['']
  def extract_keywords_from_text(self, s, threshold = 50, n = 5, length = 1, is_print = True, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, random_cnt = 1):
    ma = natural_language_processing.MA.get_mecab_coupled(s)
    return self.extract_keywords_from_ma(ma = ma, threshold = threshold, n = n, length = length, is_print = is_print, needs = needs, random_cnt = random_cnt)
  def extract_keywords_from_ma(self, ma, threshold = 50, n = 5, length = 1, is_print = True, needs = {'名詞', '固有名詞', '動詞', '形容詞'}, random_cnt = 1):
    def keyword_filter(datas):
      exception_set = {'ちゃん'}
      return [data for data in datas if not data[0] in exception_set]

    keyword_tf_idf = self.calc_keywords_tf_idf(ma, length = length, needs = needs)
    kwcnt = len(keyword_tf_idf)
    keyword_tf_idf = keyword_filter(keyword_tf_idf)
  
    if random_cnt > 0:
      return self.get_random_keywords(keyword_tf_idf, random_cnt = random_cnt)
    if kwcnt == 0:
      if is_print:
        print('=> キーワードは見つかりませんでした。')
      return ['']
    else:
      if is_print:
        if kwcnt < n:
          print('=> ' + str(kwcnt) + '個の文章の重要キーワードを抽出しました。')
        else:
          print('=> ' + str(n) + '個の文章の重要キーワードを抽出しました。')
      mostImptf_idf = keyword_tf_idf[0][2]
      print(mostImptf_idf)
      convImpRate = 100 / float(mostImptf_idf)
  
      return impkey
  
  def calc_cosine_similarity(self, s1, s2):
    try:
      intexts = [s1, s2]
      tf_idf_ls = [{ma[7]: ma[10] for ma in self.extract_tf_idf(natural_language_processing.MA.get_mecab_coupled(text)) if ma[1] in {'動詞', '名詞', '固有名詞', '形容詞', '助詞', '副詞', '助動詞'}} for text in intexts]
      vecF = set(_.f7(list(chain.from_iterable([tf_idf_ls[0].keys()] + [tf_idf_ls[1].keys()]))))
      tf_idf_ls0 = tf_idf_ls[0]
      tf_idf_ls1 = tf_idf_ls[1]
      v1 = np.array([tf_idf_ls0[w] if w in set(tf_idf_ls0) else 0 for w in vecF])
      v2 = np.array([tf_idf_ls1[w] if w in set(tf_idf_ls1) else 0 for w in vecF])
      bunbo = (np.linalg.norm(v1) * np.linalg.norm(v2))
      if bunbo:
        return np.dot(v1, v2) / bunbo
      else:
        return 0
    except Exception as e:
      print(e)
      return 0
TFIDF = TFIDF()
class TrigramMarkovChain(MyObject):
    def __init__(self, character = 'sys'):
        self.character = character
        self.selected_character_database = []
    def generate(self, word, is_randomize_metasentence = True):
        ans = ''
        try:
            with talk_sql.transaction():
                metaframe = self.get_metasentence()
                if '助詞,' in metaframe:
                    metaframe = [''.join([f, '助詞']) if f[-1] != '>' else f for f in metaframe.split('助詞,')][0]
                self.selected_character_database = TrigramModel.select().where(TrigramModel.character == self.character)
                try:
                    backward_ans = self.generate_backward(startWith = word)
                except Exception as e:
                    p(e)
                # backward_ans = '' 
                try:
                    forward_ans = self.generate_forward(word, Plist = metaframe)
                except Exception as e:
                    p(e)
                ans = ''.join([backward_ans, forward_ans])
                ans = ans.replace('<BOS>', '').replace('<EOS>', '')
        except Exception as e:
            talk_sql.rollback()
        return ans
    def choose_randomword(self, Ws, place = 2):
        word_cnt_ls = [w.cnt for w in Ws]
        if not word_cnt_ls:
            return ''
        cnt_array = np.array([w.cnt for w in Ws])
        if place == 2:
            words_ls = [w.W2 for w in Ws]
        elif place == 3:
            words_ls = [w.W3 for w in Ws]
        elif place == 10:
            words_ls = [w.framework for w in Ws]
        else:
            words_ls = [w.W1 for w in Ws]
        return np.random.choice(words_ls, p = cnt_array/np.sum(cnt_array))
    def get_metasentence(self, n = 50):
        try:
            Ms = mSentence.select().where(mSentence.framework.contains('<BOS>,名詞,助詞')).order_by(mSentence.cnt.desc()).limit(n)
            return self.choose_randomword(Ms, place = 10)
        except Exception as e:
            p(e)
    def get_same_hinshi(self, hinshi):
            W = ''
            # print('品詞一致1')
            try:
                Ws = self.selected_character_database.where(TrigramModel.P1 == P1).order_by(TrigramModel.cnt.desc()).limit(n)
                W = self.choose_randomword(Ws, place = 1)
            except Exception as e:
                pass
            if not W:
                # print('品詞一致2')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.P2 == P2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 2)
                except Exception as e:
                    pass
            if not W:
                # print('品詞一致3')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.P3 == P3).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    pass
            return W
    def generate_forward(self, startWith = '', Plist = ['<BOS>','名詞','名詞','名詞','助詞','動詞','助詞','助詞','名詞','名詞','名詞','助詞','動詞','助動詞','助動詞','<EOS>'], break_set = {'」', '。', '!', '！', '?', '？'}, is_debug = False, n = 10000):
        QuestionPhrase = '<KEY>...？'
        lenP = len(Plist)
        is_correct_with_hinshi = True
        i = 0
        if startWith:
            ans = ['<BOS>', startWith]
        else:
            try:
                Ws = self.selected_character_database.where(TrigramModel.W1 == ans[0], TrigramModel.P2 == Plist[1]).order_by(TrigramModel.cnt.desc())
                W = self.choose_randomword(Ws, place = 2)
            except Exception as e:
                W = ['...']
                i+= 1
            ans = ['<BOS>', W]
        while True:
            pre1 = ans[i]
            i1 = i+1
            pre2 = ans[i1]
            if i+2 >= lenP:
                is_correct_with_hinshi = False
            else:
                P3 = Plist[i+2]
                P2 = Plist[i1]
                P1 = Plist[i]
            W = ''
            if not W and is_correct_with_hinshi:
                # print('2単語一致前方2品詞一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3, TrigramModel.P2 == P2, TrigramModel.P1 == P1).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    p(e)
                    pass
            if not W and is_correct_with_hinshi:
            # print('2単語一致前方1品詞一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3, TrigramModel.P2 == P2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    p(e)
                    pass
            if not W and is_correct_with_hinshi:
                # print('2単語一致品詞一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2, TrigramModel.P3 == P3).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    pass
            if not W and is_correct_with_hinshi:
                W = self.get_same_hinshi(P1)
            if not W:
                # print('2単語一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W1 == pre1, TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    pass
            if not W:
                # print('1単語一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 3)
                except Exception as e:
                    pass
            if not W:
                # print('1単語一致2')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W1 == pre1).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 2)
                except Exception as e:
                    if i == 0:
                        return QuestionPhrase.replace('<KEY>', pre2)
            # p(ans)
            if ans[-1] != W:
                ans.append(W)
            else:
                break
            i = i +1
            # if lenP < i+3:
            #     break
            if W == '<EOS>':
                break
            # if W in break_set:
            #     break
            # if i > 30:
            #     break
        return ''.join(ans)
#   
    def generate_backward(self, startWith = '', Plist = ['<EOS>', '名詞', '助詞', '形容詞', '顔文字','顔文字','顔文字','顔文字','顔文字','顔文字','顔文字','顔文字'], break_set = {'「', '」',  '。', '!', '！', '?', '？'}, n = 100):
        QuestionPhrase = '…'
        isAddFACE = False
        if startWith:
            ans = ['<EOS>', startWith]
        else:
            ans = ['<EOS>']
        lenP = len(Plist)
        i = 0
        is_correct_with_hinshi = True
        if len(ans) == 1:
            try:
                Ws = self.selected_character_database.where(TrigramModel.W3 == ans[0], TrigramModel.P2 == Plist[1]).order_by(TrigramModel.cnt.desc())
                W = self.choose_randomword(Ws, place = 2)
            except Exception as e:
                W = ['...']
            ans += W
            i+= 1
            p(ans)
        while True:
            pre1 = ans[i]
            i1 = i+1
            pre2 = ans[i1]
            if i+2 >= lenP:
                is_correct_with_hinshi = False
            else:
                P3 = Plist[i+2]
                P2 = Plist[i1]
                P1 = Plist[i]
            W = ''
            if not W and is_correct_with_hinshi:
              # print('2単語一致前方2品詞一致', ans, i)
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3, TrigramModel.P2 == P2, TrigramModel.P3 == P1).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 1)
                except Exception as e:
                    pass
            if not W and is_correct_with_hinshi:
                # print('2単語一致前方1品詞一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3, TrigramModel.P2 == P2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 2)
                except Exception as e:
                    pass
            if not W and is_correct_with_hinshi:
                # print('2単語一致品詞一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2, TrigramModel.P1 == P3).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 1)
                except Exception as e:
                    pass
            if not W and is_correct_with_hinshi:
                W = self.get_same_hinshi(P1)
            if not W:
                # print('2単語一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W3 == pre1, TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 1)
                except Exception as e:
                    pass
            if not W:
                # print('1単語一致')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W2 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 1)
                except Exception as e:
                    pass
            if not W:
                # print('1単語一致2')
                try:
                    Ws = self.selected_character_database.where(TrigramModel.W3 == pre2).order_by(TrigramModel.cnt.desc()).limit(n)
                    W = self.choose_randomword(Ws, place = 2)
                except Exception as e:
                    if i == 0:
                        return QuestionPhrase
            if ans[-1] != W:
              ans.append(W)
            else:
              break
            i = i +1
            if W == '<BOS>':
              break
        return ''.join(ans[2::][::-1])
    # print(e)
def updateMC(taskid = 0, character = '', taskdict = {'character':'sys'}):
  try:
    with talk_sql.transaction():
      if taskid != 0:
        t = TrigramModel.update(**taskdict).where(TrigramModel.id == taskid)
      else:
        t = TrigramModel.update(**taskdict).where(TrigramModel.character == character)
      t.execute()
  except Exception as e:
    print(e)
    talk_sql.rollback()

def saveMetaS(P):
  Pstr = ','.join(P)
  try:
    # talk_sql.create_tables([TrigramModel, mSentence], True)
    with talk_sql.transaction():
      try:
        M, created = mSentence.get_or_create(framework = Pstr)
        if created == True:
          M.framework = Pstr
          M.cnt = 1
          M.ok = 1
          M.ng = 0
          M.save()
        else:
          M.cnt = M.cnt + 1
          M.save()
      except Exception as e:
        print(e)
      talk_sql.commit()
  except Exception as e:
    talk_sql.rollback()

def save_modpair(_from, _to, _tag = ''):
  try:
    # talk_sql.create_tables([TrigramModel, mSentence, mod_pair], True)
    with talk_sql.transaction():
      try:
        M, created = mod_pair.get_or_create(w_from = _from, w_to = _to)
        if created:
          M.w_from = _from
          M.w_to = _to
          M.w_tag = _tag
          M.cnt = 1
          M.posi = 1
          M.nega = 0
          M.save()
        else:
          M.cnt = M.cnt + 1
          M.w_tag = _tag
          M.save()
      except Exception as e:
        print(e)
      talk_sql.commit()
  except Exception as e:
    talk_sql.rollback()

def get_modpair(_from = '', _to = '', _tag = '', n = 100):
  ansdic = {"from": '', "to": '', "tag": '', "cnt": ''}
  try:
    # talk_sql.create_tables([TrigramModel, mSentence], True)
    with talk_sql.transaction():
      try:
        if not _to:
          Ms = mod_pair.select().where(mod_pair.w_from == _from, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
          cntArr = np.array([m.cnt for m in Ms])
          return np.random.choice([m.w_to for m in Ms], p = cntArr/np.sum(cntArr))
        elif not _from:
          Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
          cntArr = np.array([m.cnt for m in Ms])
          return np.random.choice([m.w_from for m in Ms], p = cntArr/np.sum(cntArr))
        elif not _tag:
          Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_from == _from).order_by(mod_pair.cnt.desc()).limit(n)
          cntArr = np.array([m.cnt for m in Ms])
          return np.random.choice([m.w_tag for m in Ms], p = cntArr/np.sum(cntArr))
        else:
          Ms = mod_pair.select().where(mod_pair.w_to == _to, mod_pair.w_from == _from, mod_pair.w_tag == _tag).order_by(mod_pair.cnt.desc()).limit(n)
          return Ms[0].w_cnt
      except Exception as e:
        print(e)
      talk_sql.commit()
  except Exception as e:
    talk_sql.rollback()
    return ansdic

def trigram_main(s, is_debug = False, character = 'sys'):
  try:
    ma = natural_language_processing.MA.get_mecab_coupled(s, couple_target = {'記号', '助動詞', '助詞' ,'名詞'}, cp_kakoi = '{}', cp_splitter = '', masking_format = '{original}',  is_mask_on = 1)
    ma = [[w[0], w[1]] for w in ma]
    ma = [['<BOS>', '<BOS>']] + ma + [['<EOS>', '<EOS>']]
    Plist = [w[1] for w in ma]
    # saveMetaS(Plist)
    wcnt = len(ma)
    triMA = [(ma[i], ma[i+1], ma[i+2]) for i in range(wcnt-2)]
    if is_debug:
      p(triMA)
    # if is_learn:
    #   [save_trigram(ma, character = character) for ma in triMA]
    return triMA
  except Exception as e:
    p(e)
    return False
def learn_trigram(s_ls, character = 'sys', over = 0, save_freqcnt = 5):
  i = 1;
  try:
    # talk_sql.create_tables([TrigramModel, mSentence], True)
    with talk_sql.transaction():
      for s in s_ls[over:]:
          p('++++++++++++++++++++++++++++++++++++++++++++++++++')
          p(over+i, s)
          try:
            # trigram_main(s, 1, 1, character = character)
            trigrams = trigram_main(s, is_debug = False, character = 'sys')
            for trigram in trigrams:
              save_trigram_in_transaction(trigram, character = 'sys')
              if character != 'sys':
                save_trigram_in_transaction(trigram, character = character)
          except Exception as e:
            print(e)
            pass
          else:
            # if i % 1 == save_freqcnt:
            talk_sql.commit()
            # pass
            i += 1
  except Exception as e:
    talk_sql.rollback()
    return False
  else:
    p('complete!! all trigram-learning')
    return True
def save_trigram_in_transaction(tri, character = 'sys'):
  ma1 = tri[0]
  ma2 = tri[1]
  ma3 = tri[2]
  try:
    T, created = TrigramModel.get_or_create(character = character, W1 = ma1[0], W2 = ma2[0], W3 = ma3[0], P1 = ma1[1], P2 = ma2[1], P3 = ma1[1])
    if created:
      T.character = character
      T.W1 = ma1[0]
      T.W2 = ma2[0]
      T.W3  = ma3[0]
      T.P1  = ma1[1]
      T.P2 = ma2[1]
      T.P3 = ma3[1]
      T.cnt = 1
      T.posi = 1
      T.nega = 0
    else:
      T.cnt = T.cnt +1
    T.save()
  except Exception as e:
    return False
# def learn_trigram(s_ls, character = 'sys', over = 0):
#   i = 1;
#   for s in s_ls:
#     if i > over:
#       p('++++++++++++++++++++++++++++++++++++++++++++++++++')
#       p(i, s)
#       try:
#         trigram_main(s, 1, 1, character = character)
#       except Exception as e:
#         print(e)
#     i += 1
# def save_SyApairs(s, pair_type = ''):
#   try:
#     cadic = natural_language_processing.SyA.get_CaboCha_dic(s)
#     pairs = natural_language_processing.SyA.get_pairs(cadic, pair_type = pair_type)
#     [save_modpair(_from = pair[0], _to = pair[1][0], _tag = pair[2]) for pair in pairs]
#   except Exception as e:
    # print(e)


# def learnSyA(sList, over = 0):
#   i = 1;
#   for s in sList:
#     if i > over:
#       print('++++++++++++++++++++++++++++++++++++++++++++++++++')
#       print(i, s)
#       try:
#         save_SyApairs(s, pair_type = '')
#       except Exception as e:
#         print('')
#     i += 1

def learnLang(sList, character = 'U'):
  i = 1;
  for s in sList:
    print('++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(i, s)
    try:
      TrigramModel = trigram_main(s, 1, 0, character)
      tfidf = TFIDF.append_tf_idf_on_ma_result(s, i, True, 0)
    except Exception as e:
      print('')
    i += 1

def extractKeywords(ma, exp = {'助詞', '助動詞', '記号', '接続詞', '数'}):
  def isKeyword(x, exp = {'助詞', '助動詞', '記号', '接続詞', '数'}):
    if x[1] in exp:
      return False
    elif x[2] in exp:
      return False
    else:
      return True
  return [x for x in sorted(ma, key = lambda x: x[10], reverse = True) if isKeyword(x, exp)]

# def addRelateKW(KWdict):
#   KWdict['名詞'] = ['']
#   KWdict['<BOS>'] = [KWdict['名詞'].pop()]
#   KWdict['形容詞'] = ['危ない', '嬉しい', '汚い']
#   KWdict['格助詞'] = ['は']
#   KWdict['記号'] = ['！']
#   return KWdict

# def getSimilarWords(w = '淫夢', cnt = 3, dockerIP = '192.168.59.103'):
#   g = requests.get("http://" + dockerIP + ":22670/distance?a1=" + w).json()
#   return [g['items'][i]['term'] for i in range(cnt)]

# def getAnalogy(w = ['かわいい', '最低'], cnt = 3, dockerIP = '192.168.59.103'):
#   w.append('')
#   w1 = w[0]
#   w2 = w[1]
#   w3 = w[2]
#   if not w[2]:
#     w3 = w2
#   g = requests.get(''.join(["http://",dockerIP,":22670/analogy?a1=", w1, "&a2=", w2, "&a3=", w3])).json()
#   return [g['items'][i]['term'] for i in range(cnt)]

# def associateAns(word):
#   anal = getSimilarWords(w = word, cnt = 3, dockerIP = '192.168.59.103')
#   ans = ''.join([word, 'といえば', anal[0], 'とか', anal[1], 'ですよね。'])
#   return ans

def get_tweet_log(text = '', kws = [''], UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = [], n = 20, min_similarity = 0.2):
  try:
    if not kws[0]:
      return ''
    with twlog_sql.transaction():
      if not UserList:
        dialogs = TwDialog.select().where(TwDialog.KWs.contains(kws[0]), ~TwDialog.nameB << BlackList).order_by(TwDialog.posi.desc()).limit(n)
      else:
        dialogs = TwDialog.select().where(TwDialog.KWs.contains(kws[0]), ~TwDialog.nameB << BlackList, TwDialog.nameB << UserList).order_by(TwDialog.posi.desc()).limit(n)
      d_list = [(TFIDF.calc_cosine_similarity(s1 = text, s2 = d.textA), d.textB) for d in dialogs]
      d_listS = sorted(d_list, key = lambda x: x[0], reverse = True)
      if not d_listS[0][1]:
        return ''
      if d_listS[0][0] > min_similarity:
        return ''.join([d_listS[0][1], '\n(Log合致度:', str(d_listS[0][0]), ')'])
      else:
        return ''
  except Exception as e:
    print(e)
    twlog_sql.rollback()
    return ''
def reform_info(info, username = '@username'):
    try:
        if info['is_collapsed']:
          raise Exception
        ans = natural_language_processing.anal_info(info)
        if '？' in ans:
          ans = ''
        else:
          filler = 'なるほど...'
          ans = ''.join([filler, ans.format(username = username), ' _φ(•̀ ᴗ  •́ )'])
    except Exception as e:
        p(e)
        ans = '__ERR__'
    if '__ERR__' in ans:
        ans = ''
    return ans 

def wordnet_dialog(kw = 'テスト'):
  ans = ''
  s_order = ''
  wn ='wordnet'
  if not kw:
    return ''
  try:
    wn_dic = operate_sql.get_wordnet_result(lemma = kw)
    wn_dic_keys = ([key for key in wn_dic.keys()])
    rand_key = np.random.choice(wn_dic_keys)
    rand_ls = wn_dic[rand_key]
    while rand_ls == [kw]:
      del wn_dic[rand_key]
      rand_key = np.random.choice(wn_dic_keys)
      rand_ls = wn_dic[rand_key]
    if kw in rand_ls:
      rand_ls.remove(kw)
    if rand_key == 'hype':#上位語
      s_order = '{kw}って{wn}の一種ですよね。'
    elif rand_key == 'hypo':#下位語
      s_order = '{kw}といえば、{wn}ってその一種ですよね。'
    elif rand_key == 'mprt': #被構成要素(部分)
      s_order = '{kw}といえば、{wn}ってその一部ですよね。'
    elif rand_key == 'hprt': #構成要素(部分)
      s_order = '{kw}って{wn}の一部ですよね。'
    elif rand_key == 'mmem': #被構成要素(構成員)
      s_order = '{kw}って、{wn}で構成されてますよね。'
    elif rand_key == 'hmem': #構成要素(構成員)
      s_order = '{kw}って、{wn}を構成しますよね。'
    elif rand_key == 'dmnc': #被包含領域(カテゴリ)
      s_order = '{kw}って、{wn}のカテゴリに入りますよね。'
    elif rand_key == 'dmtc': #包含領域(カテゴリ)
      s_order = '{kw}って、{wn}のカテゴリですよね。'
    elif rand_key == 'dmnu': #被包含領域(語法)
      s_order = '{kw}って、{wn}の語法に入りますよね。'
    elif rand_key == 'dmtu': #包含領域(語法)
      s_order = '{kw}って、{wn}の語法ですよね。'
    elif rand_key == 'dmnr': #被包含領域(地域)
      s_order = '{kw}って、{wn}の地域特有のものですよね。'
    elif rand_key == 'dmtr': #包含領域(地域)
      s_order = '{kw}といえば、{wn}とかが地域特有のものですよね。'
    elif rand_key == 'msub':#被構成要素(物質・材料)
      s_order = '{kw}って、{wn}の材料ですよね。'
    elif rand_key == 'hsub':#構成要素(物質・材料)
      s_order = '{kw}って、{wn}を材料にしてつくられてますよね。'
    elif rand_key == 'enta':
      s_order = '{kw}ってことは、当然{wn}してますよね。'
    elif rand_key == 'caus':
      s_order = '{kw}ってことは{wn}するのですね。'
    elif rand_key == 'inst':
      s_order = '{kw}って、{wn}の一例ですよね。'
    elif rand_key == 'hasi':
      s_order = '{kw}って、たとえば{wn}ですよね。'
    elif rand_key == 'attr':
      s_order = '{kw}と{wn}の間にはなにか関係がありますよね。'
    elif rand_key == 'sim':
      s_order = '{kw}と{wn}は似てますよね。'
    elif rand_key == 'coordinate':#同族語
      s_order = '{kw}って、{wn}とかと同じ感じ...ですよね。'
    else:
      s_order = '{kw}って、{wn}とかに関係する？'
    wn = np.random.choice(rand_ls)
    ans = s_order.format(kw = kw, wn = wn)
    return ans
  except Exception as e:
    p(e)
    ans = ''
    return ans
class DialogObject(MyObject):
  def __init__(self, s):
    #TODO]分離
    self.nlp_datas = natural_language_processing.NLPdatas(s)
    ##
    self.nlp_data = self.nlp_datas.main
    self.keywords = self._get_keywords(s)
    if self.nlp_data.summary.function == '断定':
      self.save_fact()
  def is_fact(self):
    # talk_sql.create_tables([FactModel], True)
    try:
      with talk_sql.transaction():
        fact_dict = self.nlp_data.summary
        fact = FactModel.get(entity = fact_dict.entity, value = fact_dict.value, akkusativ = fact_dict.akkusativ, dativ = fact_dict.dativ)
        return fact
    except Exception as e:
      p(e)
      talk_sql.rollback()
      return False
  def save_fact(self):
    # talk_sql.create_tables([FactModel], True)
    try:
      with talk_sql.transaction():
        fact_dict = self.nlp_data.summary
        fact, is_created = FactModel.get_or_create(entity = fact_dict.entity, value = fact_dict.value, akkusativ = fact_dict.akkusativ, dativ = fact_dict.dativ)
        if not is_created:
          fact.cnt += 1
        else:
          fact.cnt = 1
        fact.save()
        talk_sql.commit()
        return fact, is_created
    except Exception as e:
      p(e)
      talk_sql.rollback()
      return False
  def _get_longest_split(self, s = '', split_word = '」'):
    try:
      if not split_word in s:
        return s
      else:
        s_ls = s.split(split_word)
        split_and_len = [(split, len(split)) for split in s_ls]
        s = sorted(split_and_len, key=lambda x:x[1])[-1][0]
        return s
    except:
        return s
  def _get_keywords(self, s, needs= {'名詞', '固有名詞'}):
    keywords = ''
    if not keywords:
      s = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', s)
      keywords = TFIDF.extract_keywords_from_text(s, threshold = 50, n = 5, length = 1, is_print = False, needs = needs, random_cnt = 5)
      keywords = [kw for kw in keywords if not '@' in kw] 
    return keywords
  def dialog(self, context = '', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = [], min_similarity = 0.3, character = 'sys', tools = 'SYA,WN,LOG,MC', username = '@〜〜'):
    #URL除去
    s = self.nlp_data.text
    ans = ''
    if context:
      try:
        p(context.split('</>'))
        s = context.split('</>')[-1] + s
      except:
        pass
    s = re.sub(r'(https?|ftp)(://[\w:;/.?%#&=+-]+)', '', s)
    generated_by = 'nod'
    mas = natural_language_processing.MA.get_mecab_coupled(s)
    try:
      if not self.keywords:
          kw = '私'
      else:
          kw = self.keywords[0]
      if not ans:
        if 'LOG' in tools:
          ans = get_tweet_log(text = s, kws = self.keywords, UserList = UserList, BlackList = BlackList, min_similarity = min_similarity)
          generated_by = 'LOG'
          if ans:
            character = 'sys'
      if not ans:
        if 'WN' in tools:
          ans = wordnet_dialog(kw = kw)
          generated_by = 'WN'
          if ans:
            character = '海未'
      if not ans:
        if 'MC' in tools:
          trigram_markov_chain_instance = TrigramMarkovChain(character)
          ans = trigram_markov_chain_instance.generate(word = kw, is_randomize_metasentence = is_randomize_metasentence)
          generated_by = 'MC'
      if not ans:
        raise Exception
    except Exception as e:
      p(e)
      ans = operate_sql.get_phrase(status = 'nod', character = character)
      generated_by = 'nod'
      if '...:[' in ans:
        BA = operate_sql.get_phrase(status = 'nod')
    # if is_learn:
    #   trigram_main(s, is_learn = True, is_debug = False)
    ans = self._get_longest_split(ans, split_word = '」')
    ans = self._get_longest_split(ans, split_word = '「')
    ans = self._get_longest_split(ans, split_word = '。')
    ans = self._get_longest_split(ans, split_word = '：')
    ans = self._get_longest_split(ans, split_word = '』')
    ans = self._get_longest_split(ans, split_word = '『')
    now = datetime.now()
    if '<数>秒' in ans:
      sec_str = now.strftime('%S秒')
      ans = ans.replace('<数>秒', sec_str)
    if '<数>分' in ans:
      min_str = now.strftime('%M分')
      ans = ans.replace('<数>分', min_str)
    if '<数>時' in ans:
      hour_str = now.strftime('%H時')
      ans = ans.replace('<数>時', hour_str)
    if '<数>日' in ans:
      ans = ans.replace('<数>日', '一日')
    if '<数>度' in ans:
      ans = ans.replace('<数>度', '二度')
    if '<数>回' in ans:
      ans = ans.replace('<数>回', '数回')
    if '<人名>' in ans:
      if character != 'sys':
          ans = ans.replace('<人名>', character)
      else:
          ans = ans.replace('<人名>', 'あるぱか')
    ans = self._get_longest_split(ans, split_word = '<数>')
    ans = ans.replace('<接尾>', 'さん').replace('<地域>', 'アキバ')
    ans = ans.replace('Threetwo', '').replace('Three', '').replace('one', '').replace('RaidOntheCity', '')
    if not ans[-1] in {'。', '!', '?', '！', '？'}:
      ans = ''. join([ans, '。'])
    if character != 'sys':
      ans = ''.join([character, '「', ans, '」'])
    return ans

if __name__ == '__main__':
  import sys
  import io
  import os
  sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

  command = ''
  text = '''凛ちゃんは,,,です''' 
  s_ls = operate_sql.get_twlog_list(n = 1000000, UserList = [''], contains = '')
  p(len(s_ls))
  # learn_trigram(s_ls, character = 'ことり', over = 0)
  # s_ls = ['足利さんに送信して']
  # trigram_main(s_ls[0], is_debug = True, character = '')
  # p(TFIDF.extract_keywords_from_text(text))
  # dialog_obj = DialogObject(text)
  # # reg = RegexTools.main(text)
  # # # p(reg)
  # # p(MA.get_mecab_coupled(text))
  # # # p(NLPdata(text).regex_analysis.__dict__)
  # nlp_data = dialog_obj.nlp_data
  # # p(nlp_data.summary)
  # p(dialog_obj.keywords)
  # p(nlp_data.summary.has_function('疑問'))
  # ans = operate_sql.get_phrase(status =  'yes', character = character)
  # p(ans)
  # p(dialog_obj.save_facts())
  # ans = dialog(s = text, context = 'この世をば我が世とぞ思う', is_randomize_metasentence = True, is_print = False, is_learn = False, n =5, try_cnt = 10, needs = {'名詞', '固有名詞'}, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308'], min_similarity = 0.3, character = '海未', tools = 'SYA')
  # p(wordnet_dialog(kw = 'テスト'))
