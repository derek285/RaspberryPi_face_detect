import time
import socket
import json
import cv2
import sys
import base64


pub_face_data = {"cmd":"P13","subcmd":"req",
                 "content":
                        {
                         "eigen_value":"xxxxxxxxxxxxx",#base64
                         "eigen_name":"",#""
                         "area_id":"" #random  NO depu
                        }
                }
ip = '33.22.11.00'
port = 12301


sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sk.connect((ip, port))
except:
    print("fail to connect socket server")
    sys.exit(1)
print("ckt connect success")


while True:
    frame = cv2.imread('face.jpg')
    cv2.imshow('show', frame)
    cv2.waitKey(0)
    retval, buffer = cv2.imencode('.jpeg', frame)
    base64_data = base64.b64encode(buffer)
    base64_string = base64_data.decode()
    pub_face_data['content']['eigen_value'] = str(base64_string)
    pub_face_data['content']['area_id'] = '201123275'
    

    try:
        data_dumped = json.dumps(pub_face_data)
        send_data = 'PCLIENT ' + data_dumped +'\r\n'
        
        # encode('utf-8')
        # encode('utf-8')
        # encode('utf-8')
        err_code = sk.sendall(send_data.encode('utf-8'))
        print(err_code)
    except socket.error:
        print('socket error,do reconnect')
        # make connet as function and recall
        time.sleep(3)
        #break
    except Exception as expmsg:
        print('other error occur:{expmsg}')
        break

    print("send face data")
    time.sleep(10)