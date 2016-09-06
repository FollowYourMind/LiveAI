#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sklearn
from sklearn import cross_validation, metrics, preprocessing, svm
from sklearn.externals import joblib
import tensorflow as tf
import tensorflow.python.platform
import skflow
#
from setup import *
import _
from _ import p, d, MyObject, MyException
import opencv_functions

NUM_CLASSES = 13
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

def conv_data(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/_imgswork"):
	imgdics = _.get_deeppath_dic(DIR)
	print(imgdics)
	train_label = [label for address, label in imgdics]
	train_image = [conv_image(address, DIR) for address, label in imgdics]
	train_image = np.asarray(train_image)
	train_label = np.asarray(train_label)
	return train_image, train_label

def conv_image(address, DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/_imgswork"):
	imgaddress = DIR+address
	recogresult = opencv_functions.FaceRecognition(imgaddress, isShow = False, saveStyle = '', work_dir = 'work', through = True)
	img = recogresult[0]
	img = opencv_functions.adjust_image(img, K = 0, isHC = True, size = (28, 28))
	return img.flatten().astype(np.float32)/255.0
# conv_image('CV_FACE_icon0_LL1-01_20160212003336.png', '/Users/masaMikam/OneDrive/imgs/learn/others/')
def conv_label(label):
    tmp = np.zeros(NUM_CLASSES)
    print(tmp)
    tmp[int(label)] = 1
    return tmp

### Convolutional network
def max_pool_2x2(tensor_in):
    return tf.nn.max_pool(tensor_in, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1],
        padding='SAME')

def conv_model(X, y, keep_prob = 0.5):
	keep_prob = 0.5
	X = tf.reshape(X, [-1, 28, 28, 3])
	with tf.variable_scope('conv_layer1'):
		h_conv1 = skflow.ops.conv2d(X, n_filters=32, filter_shape=[5, 5], bias=True, activation=tf.nn.relu)
		h_pool1 = max_pool_2x2(h_conv1)
	with tf.variable_scope('conv_layer2'):
	    h_conv2 = skflow.ops.conv2d(h_pool1, n_filters=64, filter_shape=[5, 5],
	                                bias=True, activation=tf.nn.relu)
	    h_pool2 = max_pool_2x2(h_conv2)
	    h_pool2_flat = tf.reshape(h_pool2, [-1, 7 * 7 * 64])
	h_fc1 = skflow.ops.dnn(h_pool2_flat, hidden_units = [1024], activation=tf.nn.relu, keep_prob=keep_prob)
	h_fc1 = tf.nn.dropout(h_fc1, keep_prob)
	return skflow.models.logistic_regression(h_fc1, y, class_weight=None)

def cnn_model(X, y):
	keep_prob = tf.placeholder(tf.float32)
	return conv_model(X, y, keep_prob = keep_prob)

### Linear classifier.
# classifier = skflow.TensorFlowLinearClassifier(
#     n_classes=NUM_CLASSES, batch_size=100, steps=1000, learning_rate=0.01)
# classifier.fit(data_train, label_train)
# score = metrics.accuracy_score(label_test, classifier.predict(data_test))
# print('Accuracy: {0:f}'.format(score))

def train(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/", save_dir = "/Users/masaMikam/OneDrive/imgs/DNNmodel2", logdir = '/Users/masaMikam/OneDrive/tmp/TFdata'):
	print('trainingLABELs... paste it to predictFunc!!\n', [clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])])
	images, labels = conv_data(DIR)
	data_train, data_test, label_train, label_test = cross_validation.train_test_split(images, labels, test_size=0.2, random_state=42)
	classifier = skflow.TensorFlowEstimator(
	    model_fn = cnn_model, n_classes=NUM_CLASSES, batch_size=10, steps=1000,
	    learning_rate=1e-4, optimizer='Adam', continue_training=True)
	# classifier = skflow.TensorFlowDNNClassifier(hidden_units=[10, 20, 10],
 #                                            n_classes=NUM_CLASSES, steps=1000,
 #                                            early_stopping_rounds=200)
	while True:
		classifier.fit(data_train, label_train, logdir=logdir)
		score = metrics.accuracy_score(label_test, classifier.predict(data_test))
		print('Accuracy: {0:f}'.format(score))
		classifier.save(save_dir)

 # ['chino', 'eri', 'hanayo', 'honoka', 'kotori', 'maki', 'niko', 'nozomi', 'rin', 'umi']
 # ['others', 'ことり', 'にこ', 'チノ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂']
def predictAns(filename  = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/rin/show.png", isShow = True, model = '/Users/masaMikam/Dropbox/Project/umiA/Data/lib/DNNmodel', work_dir = '', label = ['others', 'ことり', 'にこ', 'チノ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂']):
	classifier = skflow.TensorFlowEstimator.restore(model)
	# imgaddress = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/rin/images-10.jpeg"
	# imgaddress = '/Users/masaMikam/Dropbox/Project/umiA/Data/twimgs/20160204152357.jpg'
	img, altfilename, frame, face_flag = opencv_functions.FaceRecognition(filename, isShow = isShow, saveStyle = 'whole', work_dir = '')
	img = opencv_functions.adjust_image(img, isHC = True, K = 0, size = (28, 28))
	result = classifier.predict(img)
	anslabel = label[result]
	return anslabel, face_flag, altfilename

def train_svm(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/", save_dir = "/Users/masaMikam/OneDrive/imgs/SVMmodel.pkl", logdir = '/Users/masaMikam/OneDrive/tmp/TFdata'):
	print('trainingLABELs... paste it to predictFunc!!\n', [clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])])
	images, labels = conv_data(DIR)
	data_train, data_test, label_train, label_test = cross_validation.train_test_split(images, labels, test_size=0.2, random_state=42)
	# classifier = sklearn.
	scores = []
	# K-fold 交差検証でアルゴリズムの汎化性能を調べる
	# kfold = cross_validation.KFold(len(data_train), n_folds=10)
	# for train, test in kfold:
	# デフォルトのカーネルは rbf になっている
	clf = svm.SVC(C=2**2, gamma=2**-11, probability=True)
	# 訓練データで学習する
	clf.fit(data_train, label_train)
	# テストデータの正答率を調べる
	score = metrics.accuracy_score(clf.predict(data_test), label_test)
	scores.append(score)
	# 最終的な正答率を出す
	accuracy = (sum(scores) / len(scores)) * 100
	msg = '正答率: {accuracy:.2f}%'.format(accuracy=accuracy)
	print(msg)
	# clf.save(save_dir)
	joblib.dump(clf, save_dir) 

# def predict_svm(filename  = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/rin/show.png", isShow = True, model = "/Users/masaMikam/OneDrive/imgs/SVMmodel.pkl", work_dir = '', label = ['others', 'ことり', 'にこ', 'チノ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂'], is_force = False):
# 	img_kind = ''
# 	# img, altfilename, frame, face_flag = opencv_functions.FaceRecognition(filename, isShow = isShow, saveStyle = 'cat', work_dir = '', cascade_lib = cascade_lib_cat, frameSetting = {'thickness': 2, 'color':(204,153,153)})
# 	if face_flag:
# 		img_kind = 'cat'
# 	if not img_kind:
# 		img, altfilename, frame, face_flag = opencv_functions.FaceRecognition(filename, isShow = isShow, saveStyle = 'whole', work_dir = '', cascade_lib = cascade_lib_anime)
# 		if face_flag:
# 			img_kind = 'anime'
# 	if img_kind == 'anime' or is_force:
# 		classifier = joblib.load(model)
# 		img = opencv_functions.adjust_image(img, isHC = True, K = 0, size = (28, 28)).reshape(-1, 1)
# 		img = img.flatten().astype(np.float32)/255.0
# 		result = classifier.predict(img.reshape(1, -1))
# 		anslabel = label[result[0]]
# 		return anslabel, img_kind, altfilename
# 	elif img_kind == 'cat':
# 		anslabel = 'cat'
# 		return anslabel, img_kind, altfilename
# 	else:
# 		anslabel = 'no_face'
# 		return anslabel, img_kind, filename

def predict_svm(_id = '7aa33bfe-e6c0-4156-a4d0-7e53e88b1dd1', is_show = True, model = '/Users/masaMikam/OneDrive/imgs/SVMmodel.pkl', label = ['others', 'ことり', 'にこ', 'チノ', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂'], is_force = False):
	img_kind = ''
	result_dic = {}
	json = {}
	if not img_kind:
		result = opencv_functions.recognize_faceimage(_id = _id, is_show = False, cascade_lib = cascade_lib_cat)
		if 'extracted' in result:
			result_dic['cat'] = result
	if not img_kind:
		result = opencv_functions.recognize_faceimage(_id = _id, is_show = False, cascade_lib = cascade_lib_anime)

		if 'extracted' in result:
			result_dic['anime'] = result
	if 'anime' in result_dic or is_force:
		classifier = joblib.load(model)
		for i in range(len(result_dic['anime']['extracted'])):
			result_dic['anime']['extracted'][i]
			cvimg = result_dic['anime']['extracted'][i]['icon_cvimg']
			adjusted_img = opencv_functions.adjust_image(cvimg, isHC = True, K = 0, size = (28, 28)).reshape(-1, 1)
			adjusted_img = adjusted_img.flatten().astype(np.float32)/255.0
			result = classifier.predict(adjusted_img.reshape(1, -1))
			# predicted_prob = classifier.predict_proba(result)
			# p(predicted_prob)
			result_dic['anime']['extracted'][i]['prediction'] = result
			result_dic['anime']['extracted'][i]['label'] = label[result[0]]
			frame_setting = {'thickness': 1, 'color':(0, 0, 255), 'scale':1.1, 'overlay_id' : '832b32bb-3e2d-4bbf-9217-ff358fa8a317'}
			# 'fabdb2c9-50c7-459e-9a29-94bbcdd77381'
			framed_cvimg = opencv_functions.frame_image(cvimg = result_dic['anime']['original_cvimg'], pos = result_dic['anime']['extracted'][i]['pos'], frame_setting = frame_setting)
			result_dic['anime']['extracted'][i]['framed_cvimg'] = framed_cvimg
			json['frame_setting'] = frame_setting
			json['detection'] = 'anime'
			json['prediction'] = result_dic['anime']['extracted'][i]['label']
			result_dic['anime']['extracted'][i]['framed_id'] = opencv_functions.save_image_sql(cvimg = framed_cvimg, filename = ''.join([str(_id), '_SVMdetect', result_dic['anime']['extracted'][i]['label'], '_framed', str(i)]), url = str(_id), owner = None, json = json, compression_quality = 70, compression_format = 'jpg')
	elif 'cat' in result_dic:
		result_dic['cat']['extracted'][0]['label'] = 'cat'
		json['detection'] = 'cat'
		frame_setting = {'thickness': 1, 'color':(204,153,153), 'scale':1.1, 'overlay_id' :'fabdb2c9-50c7-459e-9a29-94bbcdd77381'}
		json['frame_setting'] = frame_setting
		framed_cvimg = opencv_functions.frame_image(cvimg = result_dic['cat']['original_cvimg'], pos = result_dic['cat']['extracted'][0]['pos'], frame_setting = frame_setting)
		result_dic['cat']['extracted'][0]['framed_id'] = opencv_functions.save_image_sql(cvimg = framed_cvimg, filename = ''.join([str(_id), '_cat', '_framed', str(0)]), url = str(_id), owner = None, json = json, compression_quality = 70, compression_format = 'jpg')

	return result_dic
if __name__ == '__main__':
	import sys, os, io
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	# 6海未 7真姫
	filename = '/Users/masaMikam/OneDrive/imgs/face/LL3/海未/CV_FACE_icon0_LL1-03_20160212165427.png'
	DIR = '/Users/masaMikam/OneDrive/imgs/learn/雪穂/'
	ans = predict_svm(_id = '7aa33bfe-e6c0-4156-a4d0-7e53e88b1dd1', is_show = 1, model = modelSVM,  label = ['others', 'ことり', 'にこ', '真姫', '凛', '希', '海未', '真姫', '穂乃果', '絵里', '花陽', '雪穂'])
	print(ans)
	if 'anime' in ans:
		p('a')
	# label, img_kind, IMGfile = machine_learning_img.predictSVM(filename  = filename, isShow = False, model = modelSVM, work_dir  = '')
	# train_svm(DIR = "/Users/masaMikam/OneDrive/imgs/learn/_work/", save_dir = DATADIR + '/lib/SVM_us3/SVMmodel3.pkl')

	# adrs = [DIR+clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])]
	# print([predictSVM(filename  =adr, isShow = 0, model = modelSVM)[0] for adr in adrs[:1]])
# 


