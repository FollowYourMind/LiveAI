import numpy as np
from sklearn import metrics
import pandas

import tensorflow as tf
from tensorflow.models.rnn import rnn, rnn_cell
import skflow
import natural_language_processing, dealSQL, _
# from sklearn.cross_validation import train_test_split
from sklearn import cross_validation
### Training data

def train(DataSet, saveDIR = "/Users/masaMikam/OneDrive/imgs/RNNtxtclass", logdir = '/tmp/tf_examples/word_rnn', splittype = 'char'):
    def average_model(X, y):
        word_vectors = skflow.ops.categorical_variable(X, n_classes = n_words,
            embedding_size = EMBEDDING_SIZE, name = 'words')
        features = tf.reduce_max(word_vectors, reduction_indices = 1)
        return skflow.models.logistic_regression(features, y)

    def rnn_model(X, y):
        """Recurrent neural network model to predict from sequence of words
        to a class."""
        # Convert indexes of words into embeddings.
        # This creates embeddings matrix of [n_words, EMBEDDING_SIZE] and then
        # maps word indexes of the sequence into [batch_size, sequence_length,
        # EMBEDDING_SIZE].
        word_vectors = skflow.ops.categorical_variable(X, n_classes = n_words,
            embedding_size = EMBEDDING_SIZE, name='words')
        # Split into list of embedding per word, while removing doc length dim.
        # word_list results to be a list of tensors [batch_size, EMBEDDING_SIZE].
        word_list = skflow.ops.split_squeeze(1, MAX_DOCUMENT_LENGTH, word_vectors)
        # Create a Gated Recurrent Unit cell with hidden size of EMBEDDING_SIZE.
        cell = rnn_cell.GRUCell(EMBEDDING_SIZE)
        # Create an unrolled Recurrent Neural Networks to length of
        # MAX_DOCUMENT_LENGTH and passes word_list as inputs for each unit.
        _, encoding = rnn.rnn(cell, word_list, dtype=tf.float32)
        # Given encoding of RNN, take encoding of last step (e.g hidden size of the
        # neural network of last step) and pass it as features for logistic
        # regression over output classes.
        return skflow.models.logistic_regression(encoding[-1], y)
    MAX_DOCUMENT_LENGTH = 140
    if splittype == 'ma':
        DataSet = [(' '.join([w[0] for w in natural_language_processing.MA.get_mecabCP(pair[0])]), pair[1]) for pair in DataSet]
    else:
        DataSet = [(' '.join(list(pair[0])), pair[1]) for pair in DataSet]
    X_train,X_test, y_train, y_test  = cross_validation.train_test_split([train[0] for train in DataSet], [train[1] for train in DataSet])
    vocab_processor = skflow.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    X_train = np.array(list(vocab_processor.fit_transform(X_train)))
    X_test = np.array(list(vocab_processor.transform(X_test)))
    n_words = len(vocab_processor.vocabulary_)
    print('Total words: %d' % n_words)
    ### Models
    EMBEDDING_SIZE = 50

    classifier = skflow.TensorFlowEstimator(model_fn=rnn_model, n_classes=3, steps=10, optimizer='Adam', learning_rate=0.01, continue_training=True)
    while True:
        classifier.fit(X_train, y_train, logdir=logdir)
        classifier.save(saveDIR)
        score = metrics.accuracy_score(y_test, classifier.predict(X_test))
        print('Accuracy: {0:f}'.format(score))

def predictAns(s, model = "/Users/masaMikam/OneDrive/imgs/RNNtxtclass",splittype = 'char'):
    MAX_DOCUMENT_LENGTH = 10
    classifier = skflow.TensorFlowEstimator.restore(model)
    vocab_processor = skflow.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    if splittype == 'ma':
        test = ' '.join([w[0] for w in natural_language_processing.MA.get_mecabCP(s)])
    else:
        test= ' '.join(list(s))
    print(test)
    test = np.array(list(vocab_processor.fit_transform(test)))
    result = classifier.predict(test)
    print(result)
    ans = ''
    return ans
if __name__ == '__main__':
    # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    ### Process vocabulary
    kusoripuBOTs = ['harurinmain874', 'J_I_U_bot']
    # CAT1 = [(tweet, 1) for tweet in dealSQL.get_twlog_list(n = 1100,UserList = kusoripuBOTs, contains = '')]
    CAT2 = [(tweet, 2) for tweet in dealSQL.get_twlog_list(n = 75,UserList = [], BlackList = kusoripuBOTs, contains = '')]
    print(CAT2)
    s = ''' ヤァーー、メーーンッ！
  ヤァーー、コテ、メン、ドォーー
園田家の朝は、気合の入った剣道の朝稽古で始まります。
跳躍素振り100回、正面素振り100回、蹲踞から立ち上がっての摺足と連続の3本抜き...。
まだ白々とした陽光も儚い早朝のこの時間。
袴のひもをぎゅっと締め、広い道場で稽古をするのは、なかなか気持ちの良いものです。
と、いう風に思えるようになったのは...いつの頃からだったでしょうか。
6月も末の初夏の候。
日の出も早いこの時期はこんな風に....暑い1日の中でも最も涼やかな気持ちのいい時間を過ごすことができます。が、これが冬ともなれば。午前5時くらいではまだ夜も明けきってはいない時刻。
暁暗の身を切るような冷たい空気の中を、身を縮ませながら道義に着替え、暖房のスイッチを入れてもほとんど聞いてこないいような、だだっ広い道場の空間を...冷たい海を切るように進むと。その裸足の足の一歩ごとに。

心底冷たい凍るような静けさが、私の身体を貫いて行きます。
小さい頃にはよく、そんな季節に...足の裏を縁どるような真っ赤なしもやけを作ってしまって。その痛みに涙する日もありました。

道場の床を踏みしめるたびに体に響くその痛みに泣きながら、足が痛いと訴えても。師範である父は「泣き言を言うな」「あとで薬を塗ればいい」と言うばかり。
朝の稽古が終わった後で、祖母が暮れる小さな肝油ドロップのやわらかな白い粒だけが....そんな時の私の心の支えでした。
朝のお稽古のご褒美にお婆上様がたった2粒だけくださる、とっておきの小さな白い甘いキャンディ。
この季節にしかもらうことのできないそれが、しもやけを治すためのビタミン剤だった頃hあ、ずいぶん後になるまで知りませんでしたが、私にとっては今も懐かしく優しい思い出です。
そして。そんな小さな涙の日々を過ぎて...。
今の私はもうそんなことでは泣きません。
足のうらだってすっかり強くなり、どんなに寒い冬が来ても、今ではしもやけだって少しもできなくなりました。
こうしてすごす早朝の稽古は、対面のない基本稽古のみ。
段位をとったころからか、いつしか付き合う師範である父の姿も見えない日が増え...道場は私一人の自己鍛錬の場となりました。
手つかずの1日がこれから始まろうとする、朝のこの時間。
まっさらな自分の心と体と向き合って...いつも。自分自身のその在り処を確かめるときです。
  ヤァーー、メーーンッ！
稽古の最後は...今日も稽古で使わせてもらった道場への感謝を込めて、床の雑巾がけをして終わりにします。
袴の裾を少しだけたくし上げて、お寺の小坊主さんのように走り回る姿は少しおかしいかもしれませんが、これでなかなか、この動作が足腰の鍛錬になるのです。
本当はμ'sのメンバーにもこれでをやってもらったら、きっとすごくいいのではないかと思うのですが...学校の道場は他の部活動で完全に埋まってますから、やはり無理でしょうね。
残念です...。

母です。道場の後、軽くシャワーを浴びて汗を流した私を、廊下で見つけて言いました。
「はい、お願いします」
私は...礼儀正しく頭を下げて、お師匠様にお願いをさせていただきます。師匠の言葉にうむはなく、それに...再来週に実力試験を控えた今朝は、μ'sの朝の練習がないので、時間はまだありますから。
母は...優しい人ですが。やはりことお稽古のこととなれば敬うべき私の師匠。お師匠様のおっしゃることにはいつも「はい」と答え、叩頭するのが弟子のあるべき姿です。

流れてくる「梅の春」の唄を聴きながら、無心に待っていると。お稽古場の窓から入る陽射しがどんどん強くなっていくのを感じました。
少しだけ緩く着付けた浴衣の木綿の生地が、汗を流したあとの素肌に心地よく。この時期はお稽古着も楽で気分が軽くなりますね。などと....余計なことがつい頭の中に浮かんできたりして。いけない...叱られる。
舞台そでに座っている母の方をちらりと盗み見ると、いつの間にか母は目をつぶってユラユラと...曲に聞き入っていました。
つい、笑いそうになって、必死で堪えます。母も陽に当たって思わず眠くなってしまったのでしょうか？
いえ、きっと、私の踊りが、及第点をもらえたゆえのことだと....そう思うことにしましょう。
もう目をつぶっていても安心していられるほどに...。

母は...この道場に生まれた一人娘で、日舞・園田流の家元です。
つまり、正確にいえば、園田家の現在の当主は母であり、武道家である父は入り婿ということになります。園田家はもとは武家ではありますが、女流の家系で、なかなか男子が生まれることがなく、たびたび親戚より婿養子をとっての家督相続があったそうです。しかし今はもうそんな時代でもなく、単に母が1人で継ぐことになっていたところに...ですから、もともとここは日舞のお家元の道場だったのが....偶然出会った父との結婚により、父のする武道場も併設することになり、離れをつぶして大きな道場を立てることになったそうです。
板張りの武道場には、片側に舞台が作られていて、いざという時はそこが日舞の舞台になりさらにふだんはその舞台の奥の壁が開くと、その先に広がる庭の向こうには的場が作られていて、舞台を射場として使い、弓道の練習をすることができるようになっています。
父は武道家、母は舞踊家。よく私は...父の跡取りのように思われるのですが。そんなわけで、本来は日舞の舞踊家としての跡取りが期待されていると言えます。
もちろん、こんな立派な舞踊場兼武道場があるわけですから、父からも跡取りが欲されているのは間違いないと思いますが。
といっても、あんな風に...居眠りしている母の様子を見ていると、まあ本当にそんなに期待されているのかどうかもわかりませんけれど...ね。フフフ。
曲が終わると同時に目を開けた母が言いました。

なるほど。そういうことでしたか。
言いにくそうに言って少し照れた様子の母を見ながら考えました。
そういえば、父の誕生日が近いです。
私はなんだか急に...嬉しくなりました。
それに。そういうことなら、今日は放課後のμ'sの練習のあとも、少しみんなと一緒に過ごす時間がとれそうです。
  わかりました。それなら、今日も私も穂乃果たちと一緒に夕食を取ってきてもかまわないでしょうか？
嬉しそうに笑いながら言ういつもの母のお気に入りの昔話に、少しだけうんざりし...私と穂乃果は母たちとは違います...でも、そう言いたくても、堂々と否定できないところがなぜか悔しくて。私は、もう学校の時間なので支度をしてきますと、早々に母の前を去りました。
私は...結婚とか、子どもとか。そんなことは全く考えられません!  そんな遠い遠い未来のことを言われても...困ります。それどころか、今、私たちは、私たちが一緒に居られるための場所を。私たちの母校・音ノ木坂学院をこの世から失わないために...そのために毎日一生懸命頑張っているのに。
全く呑気な母親です。
子の心、親知らず。
ああ。ことりがよく言うように。私は少し...苦労性なのでしょうか？


その日の練習を終えた...帰り道。
そう言いながら穂乃果がおなかをさすりあげる様子を見ていたら、思わず笑ってしまいました。
  そんな風におなかを突き出していたら、まるでタヌキのように見えますよ？
夕食の時間も過ぎて、もうすっかり暗くなった夜空に浮かぶ、少したれ目な丸顔の穂乃果タヌキ。
プッ...クスクス。そう思ったらますますタヌキに見てきて、笑いが止まらなくなりました。似てる...穂乃果のうちの裏庭においてある信楽焼の大きなおタヌキ様。小さい頃はよくおままごとの相手にして一緒に遊びましたっけ。
  す、すみません...クスクス
今日のμ'sの練習を終えて、みんなで立ち寄ったファミリーレストラン。一人だけ追加でポテトフライまで頼んで嬉しそうに食べていた穂乃果の顔が目に浮かぶと...やっぱりなぜか笑顔になってしまいます。
ピョンとひとつ跳ねて、髪を揺らした穂乃果が言いました。にっこり、真ん丸なお月様のような大きな笑顔。
  な、何をいきなり...
  そ、それは...
別にそんなことは気にしてないですよ、と言おうとして。少しだけ、寂しそうな穂乃果の顔に気がつきました。
全員徒歩通学のμ'sメンバーが、駅近くのファミレスから、それぞれ自宅のある方向へと別れて散り、最後に残ったのは...昔から家が一番の近所の幼なじみのこの2人。
私と...穂乃果でした。
しょんぼりと肩を落とす穂乃果に。
  そんなことないです。穂乃果だって、お店の手伝いがあるじゃないですか。
少し照れた顔でポリポリと頭をかいて言う穂乃果に...私は再び笑顔になってしまって。
  私ももう、当たり前ですから。お互い...自営業の娘は大変ですよね。
私はそう言って笑いながら、ふと前を見上げると。
急に周囲の暗さが増していました。
いつのまにか私たちの住む...家の近くまで歩いてきていました。
'''

    # umi = [(sss, 2) for sss in _.flatten([ss.split('。') for ss in s.split('\n')]) if sss != '']
    # print(umi)
    # CAT2 =
    DataSet = _.f7(CAT1 + CAT2)
    # # DataSet = [('そのとおり', 1), ('ちがうよ',2),()]
    modelfile = "/Users/masaMikam/OneDrive/imgs/RNNtxtcls_kusoripu3"
    train(DataSet, saveDIR = modelfile, splittype = 'chara')
    s = 'どういうこと'
    # predictAns(s, model = modelfile, splittype = 'ma')

