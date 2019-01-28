
# Detect & Read NeedleMeter

import cv2
import numpy as np
import sys

from picamera.array import PiRGBArray
from picamera import PiCamera

import logging
from logging import getLogger, StreamHandler, FileHandler, Formatter

# calculate distance from Point to line
def distancePoint(cx, cy, x1, y1, x2, y2):
    u = np.array([x2-x1, y2-y1])
    v = np.array([cx-x1, cy-y1])
    L = abs(np.cross(u,v)/np.linalg.norm(u))
    return L

# Read Meter
def ReadNeedleMeter(imgGray, max, min, origin, val_range, centerX, centerY, width, height):

    print(min)
    print(max)
    print(origin)
    print(val_range)
    print(centerX)
    print(centerY)
    print(width)
    print(height)

    dstBlur = cv2.GaussianBlur(imgGray, (5,5), 3)
    #cv2.imshow("threshold_Blur", dstBlur)

    adth = cv2.adaptiveThreshold(dstBlur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV,11, 2)
    #cv2.imshow("AdaptiveTreashold", adth)

    kernel = np.ones((2,2), np.uint8)
    eroded = cv2.erode(adth, kernel)
    cv2.imshow("threshold_eroded", eroded)

    # src = cv2.imread(path)
    # dst = cv2.Canny(img,50, 150)
    # cv2.imshow("Cannied", dst)

    lines = cv2.HoughLinesP(image=eroded, rho=3, theta=np.pi / 180, threshold=320, minLineLength=80, maxLineGap=10)
    print("line count=", len(lines))
    filtedLine = []

    src = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR)
    # Draw All Line and Filter Step1(Distance from Center)
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            cv2.line(src, (x1, y1), (x2, y2), (0,255,0), 2)
            distance = distancePoint(centerX, centerY, x1, y1, x2, y2)
            if distance < 3 :
                filtedLine.append(lines[i])
    cv2.imshow("HoughLinesP", src)

    correctedLine = []

    imgDetected = cv2.cvtColor(imgGray, cv2.COLOR_GRAY2BGR)
    # Correct and Filter Step2
    for i in range(0, len(filtedLine)):
        print(filtedLine[i])
        for x1, y1, x2, y2 in filtedLine[i]:
            #if x1 < x2 :
            #    if centerX < x1 or x2 < centerX :
            #        # skip
            #        print("skip")
            #        continue
            #else :
            #    if centerX < x2 or x1 < centerX :
            #        # skip
            #        print("skip")
            #        continue

            d1 = abs(np.linalg.norm(np.array([x1-centerX, y1-centerY])))
            d2 = abs(np.linalg.norm(np.array([x2-centerX, y2-centerY])))

            sx = x1
            sy = y1
            ex = x2
            ey = y2
            if d2 < d1 :
                sx = x2
                sy = y2
                ex = x1
                ey = y1
                # distance from center to start point(pixel)
                if 20 < d2:
                    print("skip")
                    continue
            else :
                if 20 < d1: 
                    print("skip")
                    continue
            correctedLine.append([sx,sy, ex,ey])
            cv2.arrowedLine(imgDetected, (sx, sy), (ex, ey), (255,255,0), 2)

    #slope
    average = 0.0
    dispersion = 0.0
    for i in range(0, len(correctedLine)):
        sx = correctedLine[i][0]
        sy = height - correctedLine[i][1]
        ex = correctedLine[i][2]
        ey = height - correctedLine[i][3]
        print(sx, sy, ex, ey)
        slope = np.arctan2(ey-sy, ex-sx) * 180 / np.pi
        if slope < 0 :
            buffer = slope + 360.0
            if buffer < origin:
                slope += 360.0

        average += slope
        dispersion += slope**2
        print(slope)

    # value
    linecnt = len(correctedLine)
    val = 0.0
    errormsg = ""
    if(0 < linecnt):
        average = average / linecnt
        print("ave=", average)
        dispersion = (dispersion /linecnt) - (average**2)
        print("dsp=", dispersion)
        # TODO Accuracy
        if(dispersion < 2)    :
            ratio = ((average - origin) / val_range)
            print("ratio=", ratio)

            val = (max - min) * ratio    
            print("Detected Value=", val)

            # draw value
            strval = '{:.2f}'.format(val)
            cv2.putText(imgDetected,strval,(10,50),0,2,(0,0,255))
        else:
            errormsg = "large dispersion"
            cv2.putText(imgDetected,"large dispersion",(10,50),0,2,(0,0,255))
            print("dispersion is out of range")
    else:
        errormsg = "no line"
        cv2.putText(imgDetected,"no line",(10,50),0,2,(0,0,255))
        print("no line detected")

    cv2.imshow("Detected Lines", imgDetected)
    #cv2.imwrite("detected.jpg", imgGray)
    return val, errormsg, imgDetected


# Detect Meter
def detectMeter(w, h, target, detector, kps, dps, template):

    # Convert gray scale
    gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    # Compute Feature value
    kpt, dpt = detector.detectAndCompute(gray, None)

    # Matching
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(dps,dpt, k=2)

    # Selection
    good = []
    #goodKeys = []
    for dms, dmt in matches:
        if(dms.distance < dmt.distance * 0.6) :
            good.append(dms)
            #goodKeys.append([dms])
    mpnt_s = np.float32([kps[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    mpnt_t = np.float32([kpt[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    # Uncomment to show matching graph
    #if 0 < len(goodKeys) :
    #    comp = cv2.drawMatchesKnn(template, kps, target, kpt, goodKeys, None, flags=2)
    #    cv2.imshow("Matching", comp)
    if len(good) < 10:
        return False, target

    # Perspective Transformation
    M, mask = cv2.findHomography(mpnt_s, mpnt_t, cv2.RANSAC, 3.0)
    matchesMask = mask.ravel().tolist()

    #h, w = src.shape
    pts = np.float32([[0,0],[0, h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)
    detectedInTarget = cv2.polylines(target, [np.int32(dst)], True, (0,255,0), 2, cv2.LINE_AA)

    # Cut
    invM = np.linalg.inv(M)
    warped = cv2.warpPerspective(gray, invM, (w,h))
    return True, warped

def main():
    print(sys.argv)

    # logger
    logger = getLogger("MeterReader")
    logger.setLevel(logging.DEBUG)

    hdlFormat = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    hdlStream = StreamHandler()
    hdlStream.setLevel(logging.DEBUG)
    hdlStream.setFormatter(hdlFormat)
    
    logger.addHandler(hdlStream)

    hdlFile = FileHandler("MeterReader.log", 'a')
    hdlFile.setLevel(logging.DEBUG)
    hdlFile.setFormatter(hdlFormat)

    logger.addHandler(hdlFile)

    # load calibration
    with open('calibration.ini', mode='r') as f:
        l = [s.strip() for s in f.readlines()]
        path = l[0]
        min = float(l[1])
        max = float(l[2])
        origin = float(l[3])
        val_range = float(l[4])
        centerX = int(l[5], 10)
        centerY = int(l[6], 10)
        width = int(l[7], 10)
        height = int(l[8], 10)

    print(path)
    print(min)
    print(max)
    print(origin)
    print(val_range)
    print(centerX)
    print(centerY)
    print(width)
    print(height)

    # load template
    imgTemp = cv2.imread(path,0)
    #cv2.imshow("Template", imgTemp)
    
    # A-KAZE as detector
    akaze = cv2.AKAZE_create()

    # key points and descriptor
    kps, dps = akaze.detectAndCompute(imgTemp, None)

    # Start camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # show window
    cv2.namedWindow("Camera Preview", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("Camera Preview", 0, 20)    

    cv2.namedWindow("Meter", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("Meter", 640, 20)


    cv2.namedWindow("threshold_eroded", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("threshold_eroded", 0, 560)    

    cv2.namedWindow("HoughLinesP", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("HoughLinesP", 400, 560)    

    cv2.namedWindow("Detected Lines", cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow("Detected Lines", 800, 560)    

    cv2.waitKey(100)

    # frame rate
    prevTickCount = cv2.getTickCount()
    freq = cv2.getTickFrequency()

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True) :
        image = frame.array

        # Detect Meter
        result, meter = detectMeter(width, height, image, akaze, kps, dps, imgTemp)
        if(result) :
            cv2.imshow("Meter", meter)
            # Read Value
            val, message, img = ReadNeedleMeter(meter, max, min, origin, val_range, centerX, centerY, width, height)
            if(0 < len(message)) :
                logger.debug("Read Meter Error = " + message)
            else :
                logger.debug("Read Meter Value = " + str(val))
            
        else :
            logger.debug("detectMeter result = " + str(result))

        # calculate frame rate
        tc = cv2.getTickCount()
        fps = 1/((tc - prevTickCount)/freq)
        strfps = '{:.2f}'.format(fps)
        prevTickCount = tc
        cv2.putText(image,strfps,(10,480 - 10),0,1,(0,0,255))

        cv2.imshow("Camera Preview", image)
        key = cv2.waitKey(10) & 0xff
        rawCapture.truncate(0)
        if key == 27 :  # "Esc" to stop
            break

    # Stop camera
    camera.close()

    # Close all windows
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
