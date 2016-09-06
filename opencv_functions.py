#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setup import *
import _
from _ import p, d, MyObject, MyException
from sql_models import *
import operate_sql
import qrcode
import cv2
import numpy as np
from PIL import Image as PILImage

def read_img(filename):
    return cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

def read_image_sql(_id):
    try:
        _data = BinaryBank.select().where(BinaryBank._id == _id).get()
    except DoesNotExist:
        return None
    else:
        file_bytes = np.asarray(bytearray(_data.data), dtype=np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)

def show_image(img, filename = None):
    if filename is None:
        filename = 'img'
    if not img is None:
        cv2.imshow(filename,img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def LUT_G(gamma = 0.75):
    # ガンマ変換ルックアップテーブル
    LUT_G = np.arange(256, dtype = 'uint8' )
    for i in range(256):
        LUT_G[i] = 255 * pow(float(i) / 255, 1.0 / gamma)
    return LUT_G

def LUT_HC(min_table = 50, max_table = 205):
    # ハイコントラストLUT作成
    diff_table = max_table - min_table
    LUT_HC = np.arange(256, dtype = 'uint8' )
    for i in range(0, min_table):
        LUT_HC[i] = 0
    for i in range(min_table, max_table):
        LUT_HC[i] = 255 * (i - min_table) / diff_table
    for i in range(max_table, 255):
        LUT_HC[i] = 255
    return LUT_HC


def LUT_LC(min_table = 50, max_table = 205):
    # ローコントラストLUT作成
    diff_table = max_table - min_table
    LUT_LC = np.arange(256, dtype = 'uint8' )
    for i in range(256):
        LUT_LC[i] = min_table + i * (diff_table) / 255
    return LUT_LC

def decreaseColorKmeans(img_src, K = 4):
    Z = img_src.reshape((-1,3))
    # float32に変換
    Z = np.float32(Z)
# K-Means法
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # UINT8に変換
    center = np.uint8(center)
    res = center[label.flatten()]
    img_dst = res.reshape((img_src.shape))
    return img_dst


def getAltName(filename, work_dir = '', kind1 = 'CV_', kind2 = '', kind3 = ''):
    filefw = filename.split('/')
    imgname = filefw.pop()
    if work_dir == '':
        altfilename = '/'.join(filefw + [''.join([kind1, kind2, kind3,'_',imgname])]).replace('__','_').replace('//','/')
    else:
        DIR2 = filefw.pop()
        DIR = '/'.join(filefw + [work_dir, DIR2])

        altfilename = DIR +'/'+''.join([kind1, kind2, kind3,'_',imgname]).replace('__','_').replace('//','/')
        if os.path.exists(DIR) == False:
            os.mkdir(DIR)
    return altfilename

def IMGprocess(filename, processes = ['HC', 'LC', 'LG', 'HG', 'BL', 'GN','SPN', 'HF', 'VF', 'HR', 'C64'], isSave = True, isShow = False):
    # ルックアップテーブルの生成
    # 変換
    src = cv2.imread(filename)
    imgs = {}
    if 'HC' in processes:
        imgs['HC'] = cv2.LUT(src, LUT_HC())
    if 'LC' in processes:
        imgs['LC'] = cv2.LUT(src, LUT_LC())
    if 'LG' in processes:
        imgs['LG'] = cv2.LUT(src, LUT_G(0.75))
    if 'HG' in processes:
        imgs['HG'] = cv2.LUT(src, LUT_G(1.5))
    if 'BL' in processes:
        average_square = (10,10)
        imgs['BL'] =  cv2.blur(src, average_square)
    if 'GN' in processes:
        row,col,ch= src.shape
        mean = 0
        sigma = 15
        gauss = np.random.normal(mean,sigma,(row,col,ch))
        gauss = gauss.reshape(row,col,ch)
        imgs['GN'] = src + gauss
    if 'SPN' in processes:
        row,col,ch = src.shape
        s_vs_p = 0.5
        amount = 0.004
        sp_img = src.copy()
        # Saltモード
        num_salt = np.ceil(amount * src.size * s_vs_p)
        coords = [np.random.randint(0, i-1 , int(num_salt)) for i in src.shape]
        sp_img[coords[:-1]] = (255,255,255)
        # Pepperモード
        num_pepper = np.ceil(amount* src.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i-1 , int(num_pepper)) for i in src.shape]
        sp_img[coords[:-1]] = (0,0,0)
        imgs['SPN'] = sp_img
    if 'HF' in processes: #Horizontal Flip
        imgs['HF'] = cv2.flip(src, 1)
    if 'VF' in processes: #Vertical Flip
        imgs['VF'] = cv2.flip(src, 1)
    if 'HR' in processes:
        hight = src.shape[0]
        width = src.shape[1]
        imgs['HR'] = cv2.resize(src,(int(hight/2),int(width/2)))
    if 'C4' in processes:
        imgs['C4'] = decreaseColorKmeans(src, K = 4)
    if 'C16' in processes:
        imgs['C16'] = decreaseColorKmeans(src, K = 16)
    if 'C64' in processes:
        imgs['C64'] = decreaseColorKmeans(src, K = 64)
    if isSave and processes!= []:
        [cv2.imwrite(getAltName(filename, kind1 = 'CV_', kind2 = process + '_', kind3 = ''), imgs[process]) for process in processes]
        print('[IMG_Saved]processed...', processes)
    return imgs

def adjust_image(img, isHC = True, K = 0, size = (28, 28)):
    if isHC:
        img = cv2.LUT(img, LUT_HC(min_table = 50, max_table = 205))
    if K > 0:
        img = decreaseColorKmeans(img, K = K)
    img = cv2.resize(img, size)
    return img

def FaceRecognition(filename = testpic, isShow = True, saveStyle = 'icon', work_dir = '_imgswork', frameSetting = {'thickness': 2, 'color':(0, 0, 255)}, through = False, cascade_lib = cascade_lib_anime):
    def faceProcess(faces, i, frameSetting = frameSetting):
        # flag = True
        flag = False
        F = faces[i]
        #(四角の左上のx座標, 四角の左上のy座標, 四角の横の長さ, 四角の縦の長さ)
        Ftop = F[1]
        Fbottom = Ftop + F[3]
        Fleft = F[0]
        Fright = Fleft + F[2]
        if not (Ftop<0 or Fbottom>height or  Fleft<0 or Fright>width):
            thickness = frameSetting['thickness']
            image = frame[Ftop+thickness: Fbottom-thickness, Fleft+thickness:Fright-thickness]
            margin = int(min((Fbottom-Ftop)/4, Ftop, height-Fbottom, Fleft, width-Fright))
            # p(margin)
            icon = frame[Ftop-margin:Fbottom+margin, Fleft-margin:Fright+margin]
            # cv2.rectangle(frame, (Fleft, Ftop), (Fright, Fbottom), frameSetting['color'], thickness = thickness)
            if not saveStyle:
                altfilename = filename
            else:
                altfilename = getAltName(filename, work_dir = work_dir, kind1 = 'CV_', kind2 = 'FACE_', kind3 = saveStyle + str(i))
                if saveStyle == 'icon':
                    cv2.imwrite(altfilename, image)
                else:
                    cv2.rectangle(frame, (Fleft, Ftop), (Fright, Fbottom), frameSetting['color'], thickness = thickness)
                    cv2.imwrite(altfilename, frame)
        else:
            image = frame 
            altfilename = filename
        if isShow:
            cv2.imshow('img',frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return image, altfilename, frame
    # ++++++++++++++++++++++++++
    frame = cv2.imread(filename)
    face_detector = cv2.CascadeClassifier(cascade_lib)
    grayimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(grayimg, scaleFactor = 1.1, minNeighbors = 5, minSize = (24, 24))
    height, width = grayimg.shape[:2]
    facecnt = len(faces)
    if facecnt == 0:
        return frame, filename, frame, False
    else:
        try:
            results = [faceProcess(faces, i) for i in range(facecnt)]
            # maxSIZE
            maxicon = results[0]
            return maxicon[0], maxicon[1], maxicon[2], True
        except Exception as e:
            print(e)
            return frame, filename, frame, False

def recognize_faceimage(_id = '7aa33bfe-e6c0-4156-a4d0-7e53e88b1dd1', is_show = True, cascade_lib = cascade_lib_anime, frame_setting = None):
    result_dic = {}
    def extract_face(faces, i):
        #(四角の左上のx座標, 四角の左上のy座標, 四角の横の長さ, 四角の縦の長さ)
        pos = faces[i]
        bottom = pos[1]+pos[3]
        right = pos[0]+pos[2]
        if not (pos[1] < 0 or right > height or pos[0] < 0 or bottom > width):
            cvimg = original_cvimg
            result_dic['extracted'] = {}
            result_dic['extracted'][i] = {}
            pos_dic = {}
            pos_dic['left'] = int(pos[0])
            pos_dic['top'] = int(pos[1])
            pos_dic['bottom'] = int(bottom)
            pos_dic['right'] = int(right)
            pos_dic['height'] = int(pos[2])
            pos_dic['width'] = int(pos[3])
            result_dic['extracted'][i]['pos'] = pos_dic
            face_icon = cvimg[pos_dic['top']: pos_dic['bottom'], pos_dic['left']: pos_dic['right']]
            if not frame_setting is None:
                framed_cvimg = frame_image(cvimg, pos = result_dic['extracted'][i]['pos'],frame_setting = frame_setting)
                show_image(framed_cvimg, filename = '')
            json = {}
            json['pos'] = result_dic['extracted'][i]['pos']
            p(json)
            result_dic['extracted'][i]['icon_cvimg'] = face_icon
            result_dic['extracted'][i]['icon_id'] = save_image_sql(cvimg = face_icon, filename = ''.join([str(_id), '_icon', str(i)]), url = _id, owner = None, json = json, compression_quality = 70, compression_format = 'jpg')
            is_show = False
            if is_show:
                show_image(face_icon, filename = result_dic[i]['icon_id'])
    # ++++++++++++++++++++++++++
    # frame = cv2.imread(filename)
    original_cvimg = read_image_sql(_id = _id)
    result_dic['original_id'] = _id
    result_dic['original_cvimg'] = original_cvimg
    face_detector = cv2.CascadeClassifier(cascade_lib)
    gray_cvimg = cv2.cvtColor(original_cvimg, cv2.COLOR_BGR2GRAY)
    result_dic['gray_cvimg'] = gray_cvimg
    faces = face_detector.detectMultiScale(gray_cvimg, scaleFactor = 1.1, minNeighbors = 5, minSize = (24, 24))
    height, width = gray_cvimg.shape[:2]
    face_cnt = len(faces)
    try:
        # No face
        if face_cnt > 0:
            [extract_face(faces, i) for i in range(face_cnt)]
        return result_dic
    except:
        _.log_err()
        return result_dic

def preIMGprocess(DIR = "/Users/masaMikam/Dropbox/Project/umiA/Data/imgs/", work_dir = 'face', processes = [], isFaced = True):
    imgdics = _.get_deeppath_dic(DIR)
    print(imgdics)
    if isFaced == False:
        [FaceRecognition(filename = DIR+address, isShow = False, saveStyle = 'icon', work_dir = work_dir) for address, label in imgdics]
    workPATH = DIR + work_dir + '/'
    print(workPATH)
    facedics = _.get_deeppath_dic(workPATH)
    print(facedics)
    [IMGprocess(filename = workPATH+address, isSave = True, processes = processes) for address, label in facedics]

# def passzbar(image): 
#     # zbar command
#     ZBARIMG = '/usr/local/bin/zbarimg'
#     # convert to bmp binary so that zbar can handle it
#     retval, buf = cv2.imencode('.bmp', image)
#     if retval == False:
#         raise ValueError('The Given image could not be converted to BMP binary data')
#     # convert buf from numpy.ndarray to bytes
#     binbmp = buf.tobytes()
#     optionargs = []
    
#     args = [ZBARIMG, ':-', '-q'] + optionargs
#     p = subprocess.Popen(
#         args,
#         stdin=subprocess.PIPE,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         shell=False,
#         close_fds=True
#     )
#     stdout, stderr = p.communicate(input=binbmp)
#     if len(stderr) == 0:
#         bindata = stdout
#     else:
#         raise RuntimeError('ZBar threw error:\n' + stderr.decode('utf-8'))
#     zans = bindata.split(b":", 1)
#     if len(zans) == 2:
#         return True, zans
#     else:
#         return False, ['', '']
def passzbar(image): 
    # zbar command
    ZBARIMG = '/usr/local/bin/zbarimg'
    # convert to bmp binary so that zbar can handle it
    retval, buf = cv2.imencode('.bmp', image)
    if retval == False:
        raise ValueError('The Given image could not be converted to BMP binary data')
    # convert buf from numpy.ndarray to bytes
    binbmp = buf.tobytes()
    optionargs = []
    
    args = [ZBARIMG, ':-', '-q'] + optionargs
    p = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        close_fds=True
    )
    stdout, stderr = p.communicate(input=binbmp)
    if len(stderr) == 0:
        bindata = stdout
    else:
        raise RuntimeError('ZBar threw error:\n' + stderr.decode('utf-8'))
    zans = bindata.split(b":", 1)
    if len(zans) == 2:
        return True, zans
    else:
        return False, ['', '']
def make_qrcode(data = 'hello', owner = None):
    try:
        qr = qrcode.QRCode(error_correction = qrcode.constants.ERROR_CORRECT_L)
        qr.add_data(data)
        qr.make(fit=True)
        cvimg = qr.make_image()
        filepath = '/'.join([_.get_thispath(), 'qr.png'])
        cvimg.save(filepath)
        _id = operate_sql.file2db(filepath = filepath, filename = None, _format = None, owner = owner)
        return _id, filepath
    except Exception as e:
        _.log_err()
        return ''

def hudist(f1 , f2):
    def h2m(x):
        if x==0:
            return 0.0
        elif x>0:
            return 1.0/np.log(x)
        else:
            return -1.0/np.log(-x)
    def hum(f):
        img = cv2.imread(f)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        moments = cv2.moments(img)
        return cv2.HuMoments(moments)
    hu = hum(f1)
    hu2 = hum(f2)
    d = np.sum([abs(h2m(x1)-h2m(x2)) for (x1,x2) in zip(hu.T[0],hu2.T[0])])
    return d

@db.atomic()
def save_image_sql(cvimg, filename = None, url = None, owner = None, json = {}, compression_quality = 70, compression_format = 'jpg'):
    compression_params = [cv2.IMWRITE_JPEG_QUALITY, compression_quality]
    retval, buf = cv2.imencode(''.join(['.', compression_format]), cvimg, compression_params)
    if url is None:
        pass
    elif filename is None:
        filename = ''.join([str(url), '_', datetime.now(JST).strftime('%Y%m%d%H%M%S')])
    if not '.' in filename:
        filename = '.'.join([filename, compression_format])
    if not retval:
        raise ValueError('The Given image could not be converted to BMP binary data')
    bin_data = buf.tobytes()
    if not json is None:
        json['compression_quality'] = compression_quality
        json['compression_format'] = compression_format
    try:
        sql_data = BinaryBank.create(_id = uuid.uuid4(), filename = filename, _format = compression_format, url = str(url), data = bin_data, owner = owner, json = json)
        return sql_data._id
    except:
        _.log_err()
def resize_image(image, height, width):
    # 元々のサイズを取得
    org_height, org_width = image.shape[:2]
    # 大きい方のサイズに合わせて縮小
    # ratio = max(float(height)/org_height, float(width)/org_width)*mod
    # リサイズ
    resized = cv2.resize(image,(int(org_height*float(height)/org_height), int(org_width*float(width)/org_width)))
    return resized 
def overlay_on_part(src_image, overlay_image, posX, posY):

    # オーバレイ画像のサイズを取得
    ol_height, ol_width = overlay_image.shape[:2]

    # OpenCVの画像データをPILに変換
    #　BGRAからRGBAへ変換
    src_image_RGBA = cv2.cvtColor(src_image, cv2.COLOR_BGR2RGB)
    overlay_image_RGBA = cv2.cvtColor(overlay_image, cv2.COLOR_BGRA2RGBA)

    #　PILに変換
    src_image_PIL= PILImage.fromarray(src_image_RGBA)
    overlay_image_PIL = PILImage.fromarray(overlay_image_RGBA)

    # 合成のため、RGBAモードに変更
    src_image_PIL = src_image_PIL.convert('RGBA')
    overlay_image_PIL = overlay_image_PIL.convert('RGBA')

    # 同じ大きさの透過キャンパスを用意
    tmp = PILImage.new('RGBA', src_image_PIL.size, (255, 255,255, 0))
    # 用意したキャンパスに上書き
    tmp.paste(overlay_image_PIL, (int(posX), int(posY)), overlay_image_PIL)
    # オリジナルとキャンパスを合成して保存
    result = PILImage.alpha_composite(src_image_PIL, tmp)

    return  cv2.cvtColor(np.asarray(result), cv2.COLOR_RGBA2BGRA)

def frame_image(cvimg, pos, frame_setting = {'thickness': 2, 'color':(0, 0, 255), 'scale':1.1, 'overlay_id' :'832b32bb-3e2d-4bbf-9217-ff358fa8a317'}):
            #face領域を囲う
    #しいたけ '74d58053-232c-40bd-88a0-daddfa1df2d7'

    height, width = cvimg.shape[:2]
    if 'thickness' in frame_setting and 'color' in frame_setting:
        cv2.rectangle(cvimg, (pos['left'], pos['top']), (pos['right'], pos['bottom']), frame_setting['color'], thickness = frame_setting['thickness'])
    if 'scale' in frame_setting:
        hinc = int(pos['height']*(frame_setting['scale'] - 1))
        winc = int(pos['width']*(frame_setting['scale']-1))
        pos['original'] = pos
        pos['left'] = pos['left']-hinc
        pos['top'] = pos['top']-hinc
        pos['bottom'] = pos['bottom']+winc
        pos['right'] = pos['right']+winc
        pos['height'] = pos['height'] + hinc + winc
        pos['width'] = pos['width'] + hinc + winc
    if 'overlay_id' in frame_setting:
        overlay_image = read_image_sql(_id = frame_setting['overlay_id'])
        overlay_image_resized = resize_image(image = overlay_image, height = pos['height'], width = pos['width'])

        cvimg = overlay_on_part(src_image = cvimg, overlay_image = overlay_image_resized, posX = pos['left'], posY = pos['top'])
    # framed_id = save_image_sql(cvimg = cvimg, filename = ''.join([_id, '_framed', str(LTRB)]), url = _id, owner = None, compression_quality = 70, compression_format = 'jpg')`
    return cvimg

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    filename = "/Users/masaMikam/Downloads/CV_FACE_icon1_46481697.jpeg"
    # filename2 = '/Users/masaMikam/Downloads/46481697.jpeg'
    # make_qrcode(data = 'hello')
    _id = '832b32bb-3e2d-4bbf-9217-ff358fa8a317'
    # cvimg = read_image_sql(_id = _id)
    # p(passzbar(cvimg))
    # _ID = save_image_sql(cvimg, filename = None, url = 'MjAxNjA5MDUwMzE5MzYvNDUyNDA=', owner = None, compression_quality = 70, compression_format = 'jpg')
    result = recognize_faceimage(_id = '7aa33bfe-e6c0-4156-a4d0-7e53e88b1dd1', is_show = True,cascade_lib = cascade_lib_anime)
    p(result)
    # p(uuid.uuid4())
    # p(uuid.uuid4().hex)
    # make_qrcode(data = 'hello', owner = None)
    # height, width = img.shape[:2]
    # p(height * width)
    # compression_params = [cv2.IMWRITE_JPEG_QUALITY, 70]
    # retval, buf = cv2.imencode('jpg', img, compression_params)
    # if not retval:
    #     raise ValueError('The Given image could not be converted to BMP binary data')
    # height, width = buf.shape[:2]
    # p(height * width)
    # # convert buf from numpy.ndarray to bytes
    # binary = buf.tobytes()
    # BinaryBank.create_or_get(filename = 'test',data = binary)
    # p(type(img))
    # show_image(img)
    # sql_data = BinaryBank.select().where(BinaryBank._id == 'MjAxNjA5MDUwMjMzNTIvNDQ1Mw==').get()
    # p(type(sql_data.data))
    # img = cv2.imread(filename2)
    # p(img)
    # imgdata = img

    # xml = cascade_lib_anime
    # ans  = FaceRecognition(filename = filename, isShow = True, saveStyle = 'icon', work_dir = 'Downloads', frameSetting = {'thickness': 2, 'color':(0, 0, 255)}, through = False, cascade_lib = xml)
    # p(ans)

    # print(hudist(filename, filename2))
    # img, altfilename, frame, flag = FaceRecognition(filename, isShow = 0, saveStyle = '', work_dir = '')
    # print(img)
    # preIMGprocess(DIR = "/Users/masaMikam/OneDrive/imgs/learn/", work_dir ='_work', isFaced = True, processes =['VF', 'HF'])
    # IMGprocess(filename, isSave = True)
    # main()





