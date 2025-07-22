# from cvzone.HandTrackingModule import HandDetector
# import cv2
import cv2
from cvzone.HandTrackingModule import HandDetector
# import os
# os.chdir("Presentation")
import os
import numpy as np

# Parameters
width, height = 1280, 720
gestureThreshold = 300
folderPath = "Presentation"
# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
# Hand Detector
detectorHand = HandDetector(detectionCon=0.8, maxHands=2)
scale = 0
# Variables
startDis = None
imgList = []
delay = 30
buttonPressed = False
counter = 0
drawMode = False
imgNumber = 0
delayCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # width and height of small image

# Get list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)
#zoom
def zoom(img,zoom_factor=2):
    return cv2.resize(img,None,fx=zoom_factor,fy=zoom_factor)

startDis = None

while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    # img1 = cv2.imread(imgCurrent)
    
    

    # Find the hand and its landmarks
    hands, img = detectorHand.findHands(img)  # with draw
    # print(hands)
    # Draw Gesture Threshold line
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:  # If hand is detected

        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]  # List of 21 Landmark points
        fingers = detectorHand.fingersUp(hand)  # List of which fingers are up
        

        # Constrain values for easier drawing
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height-150], [0, height]))
        indexFinger = lmList[8][0],lmList[8][1]

        if cy <= gestureThreshold:  # If hand is at the height of the face
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                buttonPressed = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                buttonPressed = True
                if imgNumber < len(pathImages) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

        if len(hands) == 2:
        # print("Zoom Gesture")
        # print(detector.fingersUp(hands[0]), detector.fingersUp(hands[1]))
            hand1 = hands[0]
            hand2 = hands[1]

            hand1_fingers = detectorHand.fingersUp(hands[0])
            hand2_fingers = detectorHand.fingersUp(hands[1])

            if hand1_fingers == [1,1,0,0,0] and hand2_fingers == [1,1,0,0,0]:
                lmList1 = hand1["lmList"]
                lmList2 = hand2["lmList"]

                if startDis is None:
                    # length, info, img = detectorHand.findDistance(lmList1[8], lmList2[8], img)
                    length, info, img = detectorHand.findDistance(hand1["center"], hand2["center"], img)
                    # print(length)
                    startDis = length

                # length, info, img = detectorHand.findDistance(lmList1[8], lmList2[8], img)
                length, info, img = detectorHand.findDistance(hand1["center"], hand2["center"], img)
                scale = int((length - startDis)//2)
                cx, cy = info[4:]
                # print(scale)
            else:
                startDis = None
        if fingers == [0,0,1,0,0]:
            print("beep")
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 20, (0, 0, 255), cv2.FILLED)    
        
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            print(annotationNumber)
            annotations[annotationNumber].append(indexFinger)
            cv2.circle(imgCurrent, indexFinger, 40, (0, 0, 255), cv2.FILLED)

        else:
            annotationStart = False

        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    else:
        annotationStart = False

    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False

    for i, annotation in enumerate(annotations):
        for j in range(len(annotation)):
            if j != 0:
                # print(annotation[i],annotation[j])
                cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 40)


    try:
        h1, w1, _ = imgCurrent.shape
        newH, newW = ((h1 + scale)//2)*2 , ((w1 + scale)//2)*2
        imgCurrent = cv2.resize(imgCurrent,(newH, newW))
        img[cy - newH//2 : cy + newH//2, cx - newW//2 : cx + newW//2] = imgCurrent
    
    except:
        pass
    


    # imgSmall = cv2.resize(img, (ws, hs))
    # h, w, _ = imgCurrent.shape
    # imgCurrent[0:hs, w - ws: w] = imgSmall

    cv2.namedWindow("Slides",cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Slides",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Slides", imgCurrent)
    cv2.imshow("Image", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
