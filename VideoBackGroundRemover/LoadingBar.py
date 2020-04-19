import time
import os

class LoadingBar():

	def __init__(self):
		self.CurrentProgress = 0
		self.Text = ""
		self.TotalNum = 1
		self.Resolution = 100
		self.LastUpdateTime = 0
		self.SetupDone = False
		return

	def Setup(self, text, totalNum, ShowTimer=True):
		self.Text = text
		self.TotalNum = totalNum
		self.ShowTimer = ShowTimer
		self.StartTime = time.time()
		self.SetupDone = True
		return

	def Update(self, numDone):
		if not (self.SetupDone):
			return

		if self.TotalNum == 0:
			progress = 1
		else:
			progress = numDone/self.TotalNum
			
		progress = max(progress, 0)
		progress = min(progress, 1)

		progress = int(progress*self.Resolution)

		if time.time()-self.LastUpdateTime >= 0.15 or progress == self.Resolution:
			if os.name == "nt":
				os.system('cls')
			else:
				os.system('clear')

			if progress != self.CurrentProgress:
				bar = "#"*progress
				fill = " "*(self.Resolution-progress)
				print("|"+bar+fill+"|")
				self.CurrentProgress = progress

				output = self.Text
				if output != "":
					output += "  "

				output += str(round(progress, 2))+"%  "

				if self.ShowTimer:
					output += "Time: "+str(time.time()-self.StartTime)+"s  "

				output += str(numDone)
				output += "/"
				output += str(self.TotalNum)

				print(output)

				self.LastUpdateTime = time.time()
		return