from PIL import Image
import os, sys

def ResizeImage(path, newResolution):
	img = Image.open(path)
	newImg = img.resize(newResolution, Image.ANTIALIAS)

	filePath, extension = os.path.splitext(path)
	newImg.save(filePath + "_" + str(newResolution[0]) + "x" + str(newResolution[1]) + ".png", "png")

	return

def ResizeFolder(path, newResolution):

	files = os.listdir(path)

	for file in files:

		address = os.path.join(path, file)
		if os.path.isfile(address):
			ResizeImage(address, newResolution)

		else:
			ResizeFolder(address, newResolution)

	return


if __name__ == "__main__":

	path = sys.argv[1]

	newResolution = (int(sys.argv[2]), int(sys.argv[3]))

	print("path: " + path)
	print("newResolution: " + str(newResolution))
	ResizeFolder(path, newResolution)