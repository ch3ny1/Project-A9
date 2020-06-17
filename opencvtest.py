import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    #gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    # Display the resulting frame
    #gray = cv.rectangle(frame,(960,575),(990,595),(0,0,255),2)
    #gray = cv.rectangle(gray,(1310,750),(1340,770),(0,0,255),2)
    indicator = frame[575:595,960:990,0:3]
    checker = frame[750:770, 1310:1340,0:3]
    cv.imshow('frame', indicator)
    cv.imshow('checker',checker)
    if cv.waitKey(1) == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv.destroyAllWindows()