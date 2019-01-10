import cv2
import numpy as np
import sys

from picamera.array import PiRGBArray
from picamera import PiCamera

def distancePoint(cx, cy, x1, y1, x2, y2):
    u = np.array([x2-x1, y2-y1])
    v = np.array([cx-x1, cy-y1])
    L = abs(np.cross(u,v)/np.linalg.norm(u))
    return L

def ReadNeedleMeter(imgGray, max, min, origin, val_range, centerX, centerY, width, height):

    print(min)
    print(max)
    print(origin)
    print(val_range)
    print(centerX)
    print(centerY)
    print(width)
    print(height)

    th6, dst6 = cv2.threshold(imgGray, 125, 255, cv2.THRESH_BINARY_INV)

    # src = cv2.imread(path)
    # dst = cv2.Canny(img,50, 150)
    # cv2.imshow("Cannied", dst)

    lines = cv2.HoughLinesP(image=dst6, rho=3, theta=np.pi / 180, threshold=200, minLineLength=20, maxLineGap=10)
    print("line count=", len(lines))
    filtedLine = []

    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            #cv2.line(src, (x1, y1), (x2, y2), (0,255,0), 2)
            distance = distancePoint(centerX, centerY, x1, y1, x2, y2)
            if distance < 2 :
                filtedLine.append(lines[i])
    #cv2.imshow("HoughLinesP", src)

    correctedLine = []

    for i in range(0, len(filtedLine)):
        print(filtedLine[i])
        for x1, y1, x2, y2 in filtedLine[i]:
            if x1 < x2 :
                if centerX < x1 or x2 < centerX :
                    # skip
                    print("skip")
                    continue
            else :
                if centerX < x2 or x1 < centerX :
                    # skip
                    print("skip")
                    continue

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
            correctedLine.append([sx,sy, ex,ey])

            cv2.arrowedLine(imgGray, (sx, sy), (ex, ey), (0,255,0), 2)

    cv2.imshow("Detected Lines", imgGray)
    #cv2.imwrite("detected.jpg", img)

    #slope
    average = 0.0
    for i in range(0, len(correctedLine)):
        sx = correctedLine[i][0]
        sy = height - correctedLine[i][1]
        ex = correctedLine[i][2]
        ey = height - correctedLine[i][3]
        print(sx, sy, ex, ey)
        slope = np.arctan2(ey-sy, ex-sx) * 180 / np.pi
        if slope < 0 :
            slope += 360.0

        average += slope
        print(slope)

    # value
    linecnt = len(correctedLine)
    if(0 < linecnt):
        average = average / linecnt
        print("ave=", average)

        ratio = ((average - origin) / val_range)
        print("ratio=", ratio)

        val = (max - min) * ratio    
        print("Detected Value=", val)
    else:
        print("no line")


# 対象画像
# 検知用
def detectMeter(w, h, target, detector, kps, dps ):

    # gray scale
    gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    # 特徴量算出
    kpt, dpt = detector.detectAndCompute(gray, None)

    # matching
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(dps,dpt, k=2)

    # selection
    good = []
    for dms, dmt in matches:
        if(dms.distance < dmt.distance * 0.6) :
            good.append(dms)
    mpnt_s = np.float32([kps[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    mpnt_t = np.float32([kpt[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    if len(good) < 10:
        return False, target

    # 透視変換
    M, mask = cv2.findHomography(mpnt_s, mpnt_t, cv2.RANSAC, 3.0)
    matchesMask = mask.ravel().tolist()

    #h, w = src.shape
    pts = np.float32([[0,0],[0, h-1],[w-1,h-1],[w-1,0]]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts, M)
    detectedInTarget = cv2.polylines(target, [np.int32(dst)], True, (0,255,0), 2, cv2.LINE_AA)

    # 切り抜き
    invM = np.linalg.inv(M)
    warped = cv2.warpPerspective(gray, invM, (w,h))
    return True, warped
#    cv2.imshow('warped', warped)
#    result = cv2.drawMatchesKnn(src, kps, target, kpt, good, None, flags=2)


def main():
    print(sys.argv)

    # キャリブレーションファイル読み込み
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

    # テンプレート画像読み込み
    imgTemp = cv2.imread(path,0)
    cv2.imshow("Template", imgTemp)
    
    # 特徴量算出
    # A-KAZE
    akaze = cv2.AKAZE_create()

    # key points and descriptor
    kps, dps = akaze.detectAndCompute(imgTemp, None)

    # カメラ起動
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # frame rate
    prevTickCount = cv2.getTickCount()
    freq = cv2.getTickFrequency()

    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True) :
        image = frame.array

        # メーター検出
        result, meter = detectMeter(width, height, image, akaze, kps, dps)
        if(result) :
            cv2.imshow("Meter", meter)
            ReadNeedleMeter(meter, max, min, origin, val_range, centerX, centerY, width, height)

        # 
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

    # カメラ終了
    camera.close()

    # 画面閉じる
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
