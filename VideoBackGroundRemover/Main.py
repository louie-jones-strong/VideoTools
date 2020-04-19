import traceback
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import time


class BackgroundRemover:
	def __init__(self, maxErrorAllowed=None, errorDataBatchSize=6, errorMaskBlurValue=15):
		self.MaxErrorAllowed = maxErrorAllowed
		self.ErrorDataBatchSize = errorDataBatchSize
		self.ErrorMaskBlurValue = errorMaskBlurValue
		return
	
	def ReplaceBackGround(self, targetImage, backGroundImage, newBackgroundImage=None):
		self.TargetImage = targetImage
		self.BackGroundImage = backGroundImage

		self.NewBackgroundImage = newBackgroundImage
		if type(self.NewBackgroundImage) == type(None):
			fullW = targetImage.shape[0]
			fullH = targetImage.shape[1]
			self.NewBackgroundImage = np.zeros((fullW, fullH, 3), np.uint8)
		self.GetErrorData()

		if self.MaxErrorAllowed == None:
			self.PredictMaxErrorAllowed()
			
		self.CutOut()
		return self.OutputImage

	def GetErrorData(self):
		fullH = self.TargetImage.shape[0]
		fullW = self.TargetImage.shape[1]
		
		newHigh = int(fullH/self.ErrorDataBatchSize)
		newWidth = int(fullW/self.ErrorDataBatchSize)

		targetImage = cv2.resize(self.TargetImage, (newWidth, newHigh))
		backGroundImage = cv2.resize(self.BackGroundImage, (newWidth, newHigh))

		errorMapImg = cv2.absdiff(targetImage, backGroundImage)
		errorMapImg = cv2.cvtColor(errorMapImg, cv2.COLOR_BGR2GRAY)

		errorMapImg = cv2.medianBlur(errorMapImg, self.ErrorMaskBlurValue)

		self.Errors = errorMapImg.flatten()
		self.ErrorMapImg = cv2.resize(errorMapImg, (fullW, fullH))
		return

	def PredictMaxErrorAllowed(self):
		mean = np.mean(np.array(self.Errors))
		self.MaxErrorAllowed = mean
		return

	def CutOut(self):
		ret, mask = cv2.threshold(self.ErrorMapImg, self.MaxErrorAllowed, 255, cv2.THRESH_BINARY)
		mask_inv = cv2.bitwise_not(mask)
		img1_bg = cv2.bitwise_and(self.NewBackgroundImage, self.NewBackgroundImage, mask=mask_inv)
		img2_fg = cv2.bitwise_and(self.TargetImage, self.TargetImage, mask=mask)
		self.OutputImage = cv2.add(img1_bg,img2_fg)
		return

	def Show(self):
		cv2.imshow('errorMapImg', self.ErrorMapImg)
		cv2.imshow('outputImage', self.OutputImage)
		self.ShowErrorPlot()
		cv2.waitKey(0)
		return

	def ShowErrorPlot(self):
		plt.hist(self.Errors, bins = 100)
		plt.show()
		return


if __name__ == "__main__":
	try:

		path = "Images//"
		targetImagePath = path + "targetImage.jpg"
		backGroundImagePath = path + "backGroundImage.jpg"
		newBackgroundImagePath = path + "newBackgroundImage.jpg"

		targetImage = cv2.imread(targetImagePath)
		backGroundImage = cv2.imread(backGroundImagePath)
		newBackgroundImage = cv2.imread(newBackgroundImagePath)

		
		fullW = targetImage.shape[0]
		fullH = targetImage.shape[1]
		fullW, fullH = 1080, 1920

		targetImage = cv2.resize(targetImage, (fullH, fullW))
		backGroundImage = cv2.resize(backGroundImage, (fullH, fullW))
		newBackgroundImage = cv2.resize(newBackgroundImage, (fullH, fullW))

		backgroundRemover = BackgroundRemover()

		totalTook = time.time()
		outputImage = backgroundRemover.ReplaceBackGround(targetImage, backGroundImage, newBackgroundImage)
		totalTook = time.time()-totalTook

		if totalTook > 0:
			print("FPS: ", 1/totalTook)
		cv2.imshow('outputImage', outputImage)
		cv2.waitKey(0)
	

	except Exception as e:
		strTrace = traceback.format_exc()
		print(strTrace)
