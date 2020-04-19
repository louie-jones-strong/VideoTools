import traceback
import cv2
import numpy as np
import os
import LoadingBar
import matplotlib.pyplot as plt


class BackgroundRemover:
	MaxErrorAllowed = 0.2

	def __init__(self):
		path = "Images//"
		targetImagePath = path + "targetImage.jpg"
		backGroundImagePath = path + "backGroundImage.jpg"
		newBackgroundImagePath = path + "newBackgroundImage.jpg"
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
		self.GetErrorData()
		self.PredictMaxErrorAllowed()

		while True:
			self.CutOut()
			print("MaxErrorAllowed used: ", self.MaxErrorAllowed)
			self.Show()
			userInput = input("set MaxErrorAllowed: ")
			try:
				self.MaxErrorAllowed = float(userInput)
			except Exception as e:
				break

		return

	def GetErrorData(self):
		high = self.TargetImage.shape[0]
		width = self.TargetImage.shape[1]
		
		loadingBar = LoadingBar.LoadingBar()
		loadingBar.Setup("Gettting Error Data", high)

		self.ErrorMapImg = np.zeros((high, width, 3), np.uint8)
		self.Errors = []
		for x in range(high):
			for y in range(width):

				pixelError = self.GetColourError(self.TargetImage[x][y], self.BackGroundImage[x][y])
				self.Errors += [pixelError]
				self.ErrorMapImg[x][y] = [pixelError*255, pixelError*255, pixelError*255]

			loadingBar.Update(x)

		self.ErrorMapImg = cv2.medianBlur(self.ErrorMapImg,25)
		return

	def GetColourError(self, colour1, colour2):
		error = abs(int(colour1[0])-int(colour2[0]))
		error += abs(int(colour1[1])-int(colour2[1]))
		error += abs(int(colour1[2])-int(colour2[2]))
		return error/(255*3)

	def PredictMaxErrorAllowed(self):
		mean = np.mean(np.array(self.Errors))
		median = np.median(np.array(self.Errors))
		print("mean: ", mean)
		print("median: ", median)
		self.MaxErrorAllowed = mean
		return

	def CutOut(self):
		high = self.TargetImage.shape[0]
		width = self.TargetImage.shape[1]

		self.OutputImage = np.zeros((high, width, 3), np.uint8)

		loadingBar = LoadingBar.LoadingBar()
		loadingBar.Setup("Calculating", high)

		for x in range(high):
			for y in range(width):

				if self.ErrorMapImg[x][y][2]/255 > self.MaxErrorAllowed:
					self.OutputImage[x][y] = self.TargetImage[x][y]

				elif type(self.NewBackgroundImage) != None:
					self.OutputImage[x][y] = self.NewBackgroundImage[x][y]

			loadingBar.Update(x)
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
		backgroundRemover = BackgroundRemover()
		backgroundRemover.ReplaceBackGround()

	except Exception as e:
		strTrace = traceback.format_exc()
		print(strTrace)
