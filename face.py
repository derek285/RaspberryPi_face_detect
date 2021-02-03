import time
import cv2
import base64
import socket
import sys
import json
import threading
import queue
import numpy as np
from PIL import Image

pub_hbts = {"cmd":"P13_1","subcmd":"req"} #per 30s
pub_face_data = {"cmd":"P13","subcmd":"req",
                 "content":
                        {
                         "eigen_value":"xxxxxxxxxxxxx",#base64
                         "eigen_name":"",#""
                         "area_id":"201123275" #random  NO depu
                        }
                }
ip = '133.122.111.100'
port = 12301
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
q = queue.Queue()
face_bbox_scale = 1.2


def hash_img(img):
    a = []
    hash_img = ''
    width, height = 10,10
    img = img.resize((width, height))
    for y in range(img.height):
        b = []
        for x in range(img.width):
            pos = x,y
            color_array = img.getpixel(pos)
            color = sum(color_array)/3
            b.append(int(color))
        a.append(b)
    for y in range(img.height):
        avg = sum(a[y]) / len(a[y])
        for x in range(img.width):
            if a[y][x] >= avg:
                hash_img += '1'
            else:
                hash_img += '0'
                
    return hash_img

face_tmplt = Image.open('face.png')
face_feamap = hash_img(face_tmplt)
print('global face fea map', face_feamap)


def similar(hash1, hash2):
    # hash1 = hash_img(img1)
    # hash2 = hash_img(img2)
    differnce = 0
    for i in range(len(hash1)):
        differnce += abs(int(hash1[i])-int(hash2[i]))
    similar = 1 - (differnce/len(hash1))
    return similar


def skt_connt(sk):
    try:
        sk.connect((ip, port))
    except:
        print("fail to connect socket server")
    print("ckt connect success")


def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects


def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)


def skt_pub(img, rects):
    global face_feamap

    for x1, y1, x2, y2 in rects:
        save_region = img[y1:y2, x1:x2]

        tmp_img = Image.fromarray(cv2.cvtColor(save_region, cv2.COLOR_BGR2RGB))
        tmp_feamap = hash_img(tmp_img)

        print('similar(face_feamap, tmp_feamap)', similar(face_feamap, tmp_feamap))
        if similar(face_feamap, tmp_feamap) < 0.7:

            face_feamap = tmp_feamap

            retval, buffer = cv2.imencode('.jpeg', save_region)
            base64_data = base64.b64encode(buffer)
            base64_string = base64_data.decode()
            pub_face_data['content']['eigen_value'] = str(base64_string)
            # pub_face_data['content']['area_id'] = str(int(time.time()))

            face_dumped = json.dumps(pub_face_data)
            q.put(face_dumped)
            print('capture one face', face_dumped)
            time.sleep(1)
        else:
            print('Same face reged')


def rec_choose(rects, im_w, im_h):
    bestRects = []
    rect = rects[0]
    
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    rect[0] = (rect[0] - face_bbox_scale*w) if (rect[0] - face_bbox_scale*w > 1) else 1
    rect[1] = (rect[1] - face_bbox_scale*h) if (rect[1] - face_bbox_scale*h > 1) else 1
    rect[2] = (rect[2] + face_bbox_scale*w) if (rect[2] + face_bbox_scale*w < im_w-1) else im_w-1
    rect[3] = (rect[3] + face_bbox_scale*h) if (rect[3] + face_bbox_scale*h < im_h-1) else im_h-1

    bestRects.append(rect)
    return bestRects


index = 0
time_sum = 0.0
old_sum = 0.0
face_found = 0
no_face = 0
def pFace():
    global index
    global time_sum
    global old_sum
    global no_face

    video_src = 1
    cam = cv2.VideoCapture(video_src)

    while True:
        index += 1
        ret, img = cam.read()
        im_h, im_w, im_c = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        t = time.time()
        rects = detect(gray, cascade)
        
        dt = time.time() - t
        time_sum += dt

        vis = img.copy()
        if len( rects ) > 0:
            # if index%100 == 0 and no_face < 50:
            best_rects = rec_choose(rects, im_w, im_h)                
            draw_rects( vis, best_rects, (0, 255, 0) )
            skt_pub(vis, best_rects)
                # no_face = 0
        else:
            print('No face found')
            no_face += 1
            pass

        if index%100 == 0:
            old_sum = time_sum
            time_sum = 0.0

        if old_sum > 0.0001:
            cv2.putText( vis, 'avg det time: {} s'.format( round( old_sum/100.0, 4 ) ),
                             (20, 20), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2 )
        cv2.imshow('facedetect', vis)

        key_ret = cv2.waitKey(1)
        if (key_ret == 0):  # if delete key is pressed
            break
            cam.release()


def pHtbs():
    while True:
        data_dumped = json.dumps(pub_hbts)
        q.put(data_dumped)
        print('send one htbs', data_dumped)
        time.sleep(30)


def cons_pub():
    global sk
    while True:
        if q.qsize() > 0:
            to_consu = q.get()
            send_data = 'PCLIENT ' + to_consu +'\r\n'
            print('consume one')
            try:
                err_code = sk.sendall(send_data.encode('utf-8'))
                print(err_code)
            except socket.error:
                print('socket error,do reconnect')
                skt_connt(sk)
                time.sleep(3)
            except Exception as expmsg:
                print('other error occur:{expmsg}')
                time.sleep(3)


if __name__ == '__main__':
    #lbpcascade_frontalface_improved.xml
    cascade_fn = "./cascade_frontalface.xml"
    cascade = cv2.CascadeClassifier(cascade_fn)

    skt_connt(sk)
    
    p1=threading.Thread(target=pFace,args=())
    p2 = threading.Thread(target=pHtbs, args=())
    
    con_A=threading.Thread(target=cons_pub,args=())
    p1.start()
    p2.start()
    con_A.start()

    cv2.destroyAllWindows()
