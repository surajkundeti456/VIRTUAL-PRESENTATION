from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import numpy as np
from natsort import natsorted  # For natural filename sorting

# Parameters
width, height = 1280, 720
gestureThreshold = 300
folderPath = "Presentation"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

# Variables
delay = 30
buttonPressed = False
counter = 0
drawMode = False
imgNumber = 0
delayCounter = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # Dimensions of webcam preview on slides

# Get list of valid presentation images
pathImages = [f for f in os.listdir(folderPath) if f.endswith(('.jpg', '.png', '.jpeg'))]
pathImages = natsorted(pathImages)
print("Slides Loaded:", pathImages)

# Main loop
while True:
    # Capture frame from webcam
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Load current slide
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    # Detect hands
    hands, img = detectorHand.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and not buttonPressed:
        hand = hands[0]
        cx, cy = hand["center"]
        lmList = hand["lmList"]
        fingers = detectorHand.fingersUp(hand)

        # Get index finger position with interpolation
        xVal = int(np.interp(lmList[8][0], [width // 2, width], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height - 150], [0, height]))
        indexFinger = xVal, yVal

        # Slide Navigation
        if cy <= gestureThreshold:
            if fingers == [1, 0, 0, 0, 0]:  # Left swipe
                print("← Previous Slide")
                buttonPressed = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

            if fingers == [0, 0, 0, 0, 1]:  # Right swipe
                print("→ Next Slide")
                buttonPressed = True
                if imgNumber < len(pathImages) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False

        # Drawing Mode (Index + Middle Finger Up)
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)

        # Start Drawing (Only Index Finger Up)
        if fingers == [0, 1, 0, 0, 0]:
            if not annotationStart:
                annotationStart = True
                annotationNumber += 1
                annotations.append([])
            annotations[annotationNumber].append(indexFinger)
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
        else:
            annotationStart = False

        # Undo Drawing (3 Fingers Up)
        if fingers == [0, 1, 1, 1, 0]:
            if annotationNumber >= 0:
                annotations.pop(-1)
                annotationNumber -= 1
                buttonPressed = True

    else:
        annotationStart = False

    # Button delay logic
    if buttonPressed:
        counter += 1
        if counter > delay:
            counter = 0
            buttonPressed = False

    # Draw annotations
    if annotationNumber >= 0:
        for annotation in annotations:
            for j in range(1, len(annotation)):
                cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

    # Add webcam preview to slides
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws:w] = imgSmall

    # Display
    cv2.imshow("Slides", imgCurrent)
    cv2.imshow("Webcam", img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
