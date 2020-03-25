import os
import cv2
import numpy as np
import random
import time

class SubImage:

    def __init__(self, image):
        self.Update(image)
        return

    def Resize(self, size):
        img = cv2.resize(self.Image, (size, size))
        return SubImage(img)

    def Update(self, image):

        #image[0:image.shape[0], 0:image.shape[1]] = image.mean(axis=0).mean(axis=0)

        self.Image = image
        self.AvgColour = image.mean(axis=0).mean(axis=0)
        self.ImageShape = image.shape
        return

def nothing(x):
    pass

def LoadSubImages():
    subImages = []
    files = os.listdir("SubImages")
    for file in files:
        img = cv2.imread("SubImages\\"+file)
        subImageSize = min(img.shape[0], img.shape[1])
        img = cv2.resize(img, (subImageSize, subImageSize))
        subImages += [SubImage(img)]

    return subImages

def PasteImage(mainImage, subImage, x, y):
    w = subImage.ImageShape[1]
    h = subImage.ImageShape[0]

    mainImage[x:x+w, y:y+h] = subImage.Image
    return mainImage

def GetError(tAvg, avg):
    error = abs(avg[0]-tAvg[0])
    error += abs(avg[1]-tAvg[1])
    error += abs(avg[2]-tAvg[2])
    return error/(255*3)

class ImageMaker:
    def __init__(self, fullResSubImages):
        self.FullResSubImages = fullResSubImages
        self.SubImageSizeCache = {}
        
        self.LastSubImages = {}
        self.LastSize = -1
        return

    def UpdateSubImages(self, fullResSubImages):
        self.FullResSubImages = fullResSubImages
        self.SubImageSizeCache = {}
        
        self.LastSubImages = {}
        self.LastSize = -1
        return

    def ResizeAll(self, size):
        resizedSubImages = []

        for subImage in self.FullResSubImages:
            resizedSubImages += [subImage.Resize(size)]

        self.SubImageSizeCache[size] = resizedSubImages
        return

    def GetBestSubImage(self, tAvg, x, y, size):
        if size not in self.SubImageSizeCache:
            self.ResizeAll(size)

        bestIndex = 0
        bestError = 100000

        if self.LastSize != size:
            self.LastSubImages = {}
            lastIndex = None

        elif x in self.LastSubImages and y in self.LastSubImages[x]:
            lastIndex = self.LastSubImages[x][y]

        else:
            lastIndex = None

        subImageList = self.SubImageSizeCache[size]
        for index in range(len(subImageList)):
            avg1 = subImageList[index].AvgColour
            error = GetError(tAvg, avg1)

            if bestError > error:
                bestError = error
                bestIndex = index

            if bestError == 0:
                break
        
        if lastIndex != None:
            lastError = GetError(tAvg, avg1)
            if abs(bestError-lastError) <= -1:
                bestIndex = lastIndex

        if x not in self.LastSubImages:
            self.LastSubImages[x] = {}

        self.LastSubImages[x][y] = bestIndex
        self.LastSize = size

        return subImageList[bestIndex]

def TestShow(imageMaker, targetImage, subImageSize, fullW, fullH):
    xCount = int(fullW/subImageSize)
    yCount = int(fullH/subImageSize)

    image = np.zeros((fullW, fullH, 3), np.uint8)

    targetImage = cv2.resize(targetImage, (yCount, xCount))

    for x in range(0, xCount):
        for y in range(0, yCount):
            tAvg = targetImage[x, y]

            bestSubImage = imageMaker.GetBestSubImage(tAvg, x, y, subImageSize)

            PasteImage(image, bestSubImage, x*subImageSize, y*subImageSize)
    return image

def SplitImage(image, size):
    xCount = int(image.shape[0]/size)
    yCount = int(image.shape[1]/size)

    subImages = []
    for x in range(0, xCount):
        for y in range(0, yCount):
            subImages += [SubImage(image[x*size:x*size+size, y*size:y*size+size])]
    return subImages

def Setup():
    # if input("from video(V) from WebCam(C): ").upper() == "V":
    #     address = "VideoInput\\"+os.listdir("VideoInput")[0]
    #     cap = cv2.VideoCapture(address)
    # else:
    #     cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0)
    recordVideo = False #input("record video (T/F)").upper() == "T"
    Run(cap, recordVideo)
    return


def Run(cap, recordVideo):
    scaleFactor = 5
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    fullW = frame.shape[0]
    fullH = frame.shape[1]
    print(frame.shape)

    targetImage = cv2.resize(frame, (fullH, fullW))
    subImages = SplitImage(targetImage, 50)

    subImages = LoadSubImages()
    imageMaker = ImageMaker(subImages)

    if recordVideo:
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        rec = cv2.VideoWriter("output.avi", fourcc, 17, (fullH, fullW))

    cv2.namedWindow('Image')
    cv2.createTrackbar('Size','Image',20,100,nothing)

    while(ret):
        timeMark = time.time()
        frame = cv2.flip(frame, 1)
        cv2.imshow('Frame', frame)

        targetImage = cv2.resize(frame, (fullH, fullW))

        size = cv2.getTrackbarPos('Size','Image')*scaleFactor
        if size < scaleFactor:
            size = scaleFactor

        if size > fullW or size > fullH:
            size = min(fullH, fullW)

        #imageMaker.UpdateSubImages(SplitImage(targetImage, size))
        outputImage = TestShow(imageMaker, targetImage, size, fullW, fullH)
        cv2.imshow('Image', outputImage)

        #print("Took: "+str(time.time()-timeMark))

        if recordVideo:
            rec.write(outputImage)

        ret, frame = cap.read()
        if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
            break
    
    if recordVideo:
        rec.release()
    cap.release()
    cv2.destroyAllWindows()
    return


Setup()
