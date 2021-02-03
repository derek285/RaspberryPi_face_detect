import threading
import queue
import time
import json
import cv2
import base64


pub_hbts = {"cmd":"P13_1","subcmd":"req"} #per 30s
pub_face_data = {"cmd":"P13","subcmd":"req",
                 "content":
                        {
                         "eigen_value":"xxxxxxxxxxxxx",#base64
                         "eigen_name":"",#""
                         "area_id":"" #random  NO depu
                        }
                }


q=queue.Queue()
index = 0
def pFace():
    global index
    video_src = 1
    cam = cv2.VideoCapture(video_src)

    while True:
        index += 1
        ret, img = cam.read()
        if index % 100 == 0:
            retval, buffer = cv2.imencode('.jpeg', img)
            base64_data = base64.b64encode(buffer)
            base64_string = base64_data.decode()
            pub_face_data['content']['eigen_value'] = str(base64_string)
            pub_face_data['content']['area_id'] = '201123275'

            face_dumped = json.dumps(pub_face_data)
            q.put(face_dumped)

            cv2.imshow('face det', img)
            time.sleep(3)


def pHtbs():
    while True:
        data_dumped = json.dumps(pub_hbts)
        q.put(data_dumped)
        print('send one htbs', data_dumped)
        time.sleep(30)


def consumer():
    while True:
        if q.qsize() > 0:
            send_data = q.get()
            print('consume one ', send_data)
            # TODO


if __name__=='__main__':
    # mutex = threading.Lock()

    p1 = threading.Thread(target=pFace, args=())
    p2 = threading.Thread(target=pHtbs, args=())
    con_A = threading.Thread(target=consumer, args=())
    
    p1.start()
    p2.start()
    con_A.start()
