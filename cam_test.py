import cv2

cam = cv2.VideoCapture(1)
while 1:
    if cam.isOpened():
        ret, frame = cam.read()
        h, w, c = frame.shape
        print(w, h)
        if not ret:
            print("not ret")
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
        
cam.release()
