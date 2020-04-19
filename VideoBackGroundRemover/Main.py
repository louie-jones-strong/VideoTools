import traceback
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt
import time


class BackgroundRemover:
	MaxErrorAllowed = 0.2
	ErrorDataBatchSize = 6
	ErrorMaskBlurValue = 15

	def __init__(self):
		path = "Images//"
		targetImagePath = path + "targetImage.jpg"
		backGroundImagePath = path + "backGroundImage.jpg"
		newBackgroundImagePath = path + "newBackgroundImage.jpg"

		self.OutputPath = path + "Output.jpg"

		print(os.path.exists(targetImagePath))
		print(os.path.exists(backGroundImagePath))
		print(os.path.exists(newBackgroundImagePath))

		fullW, fullH = 1080, 1920

		targetImage = cv2.imread(targetImagePath)
		backGroundImage = cv2.imread(backGroundImagePath)
		newBackgroundImage = cv2.imread(newBackgroundImagePath)

		self.TargetImage = cv2.resize(targetImage, (fullH, fullW))
		self.BackGroundImage = cv2.resize(backGroundImage, (fullH, fullW))
		self.NewBackgroundImage = cv2.resize(newBackgroundImage, (fullH, fullW))
		return
	
	def ReplaceBackGround(self):

		totalTook = time.time()
		
		timeMark = time.time()
		self.GetErrorData()
		getErrorDataTime = time.time()- timeMark
		
		self.PredictMaxErrorAllowed()

		timeMark = time.time()
		self.CutOut()
		CutOutTime = time.time()- timeMark

		totalTook = time.time()-totalTook

		cv2.imwrite(self.OutputPath, self.OutputImage)

		print("getErrorDataTime: ", getErrorDataTime)
		print("CutOutTime: ", CutOutTime)
		if totalTook > 0:
			print("FPS: ", 1/totalTook)
		print("MaxErrorAllowed used: ", self.MaxErrorAllowed)
		self.Show()
		return

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
		#self.ShowErrorPlot()
		cv2.waitKey(0)
		return

	def ShowErrorPlot(self):
		plt.hist(self.Errors, bins = 100)
		plt.show()
		return

if __name__ == "__main__":
	try:
		backgroundRemover = BackgroundRemover()
		backgroundRemover.ReplaceBackGround()

	except Exception as e:
		strTrace = traceback.format_exc()
		print(strTrace)
