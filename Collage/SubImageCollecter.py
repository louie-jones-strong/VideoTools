import numpy
import os
import cv2 as cv
import sys

print("Load...")
screen = cv.VideoCapture(0)
ret, frame = screen.read()

hight = len(frame)/2
width = len(frame[0])/2

start = [int((width-200)/2), int((hight-200)/2)]
end = [int(width/2 + 100), int(hight/2 + 100)]


print("Press enter to save")

image_number = 0
os.system( "title " + "image number:" + str(image_number) )
while True:
	ret, frame = screen.read()

	frame = frame[start[0]:end[0], start[1]:end[1]]
	cv.imshow( "input" , frame )
	ch = cv.waitKey(1)

	if ch == 27:# record image
		cv.imwrite("SubImages//" + str(image_number) + ".png", frame)

		image_number += 1
		os.system( "title " + "image number:" + str(image_number) )

screen.release()
cv.destroyAllWindows() 