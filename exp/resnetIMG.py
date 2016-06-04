#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import cv2
from itertools import chain
from collections import namedtuple
from math import sqrt

import numpy as np
import tensorflow as tf
import tensorflow.python.platform
from sklearn import cross_validation, metrics, preprocessing
import skflow
from sklearn.externals import joblib
import opencv_functions
NUM_CLASSES = 12
IMAGE_SIZE = 28
IMAGE_PIXELS = IMAGE_SIZE*IMAGE_SIZE*3

def convData(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/_imgswork"):
    imgdics = getDeepPathDic(DIR)
    print(imgdics)
    # print(imgdics)
    # データを入れる配列
    # train_label = [convLabel(label) for address, label in imgdics]
    le = preprocessing.LabelEncoder()
    labellist = [label for address, label in imgdics]
    le.fit(labellist)
    train_label = le.transform(labellist)
    print(train_label)
    train_image = [convIMG(address, DIR) for address, label in imgdics]
    # numpy形式に変換
    train_image = np.asarray(train_image)
    train_label = np.asarray(train_label)
    return train_image, train_label
def convIMG(address, DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/_imgswork"):
    imgaddress = DIR+address
    print(imgaddress)
    # データを読み込んで28x28に縮小
    img, altfilename, frame, flag = opencv_functions.FaceRecognition(imgaddress, isShow = False, saveStyle = '', workDIR = '')
    img = cv2.resize(img, (28, 28))
    return img.astype(np.float32)/255.0
    # 一列にした後、0-1のfloat値にする
    # return img.flatten().astype(np.float32)/255.0
def convLabel(label):    
    # ラベルを1-of-k方式で用意する
    tmp = np.zeros(NUM_CLASSES)
    print(tmp)
    tmp[int(label)-1] = 1
    return tmp

def getDeepPathDic(DIR):
    def filebool(jpg):
        if jpg in set(['.DS_Store']):
            return False
        elif '.' in jpg:
            return True
        else:
            return False
    clsdirs = os.listdir(DIR)
    clsdirs = [clsdir for clsdir in clsdirs if not clsdir in set(['.DS_Store'])]
    imgdics = list(chain.from_iterable([[(''.join([clsdirs[i],'/', jpg]), i)  for jpg in os.listdir(DIR + clsdirs[i]) if filebool(jpg)] for i in range(len(clsdirs))]))
    return imgdics

def res_net(x, y, activation=tf.nn.relu):
    """Builds a residual network.
    Borrowed structure from here: https://github.com/pkmital/tensorflow_tutorials/blob/master/10_residual_network.py
    Args:
        x: Input of the network
        y: Output of the network
        activation: Activation function to apply after each convolution
    Raises:
        ValueError
            If a 2D tensor is not square, it cannot be converted to a 
            4D tensor.
    """
    LayerBlock = namedtuple(
        'LayerBlock', ['num_layers', 'num_filters', 'bottleneck_size'])
    blocks = [LayerBlock(3, 128, 32),
              LayerBlock(3, 256, 64),
              LayerBlock(3, 512, 128),
              LayerBlock(3, 1024, 256)]

    # Input check
    input_shape = x.get_shape().as_list()
    if len(input_shape) == 2:
        ndim = int(sqrt(input_shape[1]))
        if ndim * ndim != input_shape[1]:
            raise ValueError('input_shape should be square')
        x = tf.reshape(x, [-1, ndim, ndim, 1])

    # First convolution expands to 64 channels
    with tf.variable_scope('conv_layer1'):
        net = skflow.ops.conv2d(x, 64, [7, 7], batch_norm=True, activation=activation)

    # Max pool
    net = tf.nn.max_pool(
        net, [1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    # First chain of resnets
    with tf.variable_scope('conv_layer2'):
        net = skflow.ops.conv2d(net, blocks[0].num_filters,
                               [1, 1], [1, 1, 1, 1], padding='VALID')

    # Create resnets for each res blocks
    for block_i, block in enumerate(blocks):
        for layer_i in range(block.num_layers):

            name = 'block_%d/layer_%d' % (block_i, layer_i)
            with tf.variable_scope(name + '/conv_in'):
                conv = skflow.ops.conv2d(net, block.num_filters,
                                         [1, 1], [1, 1, 1, 1],
                                         padding='VALID',
                                         activation=activation,
                                         batch_norm=True)

            with tf.variable_scope(name + '/conv_bottleneck'):
                conv = skflow.ops.conv2d(conv, block.bottleneck_size,
                                         [3, 3], [1, 1, 1, 1],
                                         padding='SAME',
                                         activation=activation,
                                         batch_norm=True)

            with tf.variable_scope(name + '/conv_out'):
                conv = skflow.ops.conv2d(conv, block.num_filters,
                                         [1, 1], [1, 1, 1, 1],
                                         padding='VALID',
                                         activation=activation,
                                         batch_norm=True)

            net = conv + net

        try:
            # upscale to the next block size
            next_block = blocks[block_i + 1]
            with tf.variable_scope('block_%d/conv_upscale' % block_i):
                net = skflow.ops.conv2d(net, next_block.num_filters,
                                        [1, 1], [1, 1, 1, 1], bias=False,
                                        padding='SAME')
        except IndexError:
            pass


    net = tf.nn.avg_pool(net,
                         ksize=[1, net.get_shape().as_list()[1],
                                net.get_shape().as_list()[2], 1],
                         strides=[1, 1, 1, 1], padding='VALID')
    net = tf.reshape(
        net,
        [-1, net.get_shape().as_list()[1] *
         net.get_shape().as_list()[2] *
         net.get_shape().as_list()[3]])

    return skflow.models.logistic_regression(net, y)

def train(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/", saveDIR = "/Users/masaMikam/OneDrive/imgs/DRNmodel" ):
    print('trainingLABELs... paste it to predictFunc!!\n', [clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])])
    images, labels = convData(DIR)
    data_train, data_test, label_train, label_test = cross_validation.train_test_split(images, labels)
    # Train a resnet classifier
    classifier = skflow.TensorFlowEstimator(
    model_fn=res_net, n_classes=10, batch_size=100, steps=20000,
    learning_rate=0.001)
    while True:
        classifier.fit(data_train, label_train, logdir='/Users/masaMikam/OneDrive/tmp/TFdata')
        score = metrics.accuracy_score(label_test, classifier.predict(data_test))
        print('Accuracy: {0:f}'.format(score))
        classifier.save(saveDIR)

if __name__ == '__main__':
    import sys
    import io
    import os
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    from itertools import chain
    model = "/Users/masaMikam/OneDrive/imgs/DNNmodel2" 
    filename = '/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/maki/sr-maki-cool-shoki-go.jpg'
    DIR = '/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/hanayo/'
    # preIMGprocess(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/", workDIR ='_imgswork')

    train(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/_test/", saveDIR = "/Users/masaMikam/OneDrive/imgs/DRNmodel" )
    # adrs = [DIR+clsdir for clsdir in os.listdir(DIR) if not clsdir in set(['.DS_Store'])]

    # ans, altfilename = predictAns(filename  = adrs[27], isShow = False, model = model)
    # ans, altfilename = predictAns(filename  = filename, isShow = False, model = model)
    # print('答えは'+ans, altfilename)