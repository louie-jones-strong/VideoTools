from PIL import Image
import os, sys
import moviepy.editor as mp


def ResizeImage(path, newResolutions):
	img = Image.open(path)

	for newResolution in newResolutions:
		newImg = img.resize(newResolution, Image.ANTIALIAS)

		newImg.save(NewAddress(path, newResolution, ".png"), "png")
	return

def ResizeVideo(path, newResolutions):
	video = mp.VideoFileClip(path)

	for newResolution in newResolutions:
		newVideo = video.resize(height=newResolution[0], width=newResolution[1])

		newVideo.write_videofile(NewAddress(path, newResolution, ".mp4"))
	return

def NewAddress(path, newResolution, extension):
	filePath, extension = os.path.splitext(path)
	return filePath + "_" + str(newResolution[0]) + "x" + str(newResolution[1]) + extension

def ResizeFolder(path, files, newResolutions):

	for file in files:

		address = os.path.join(path, file)

		if os.path.isfile(address):
			filePath, extension = os.path.splitext(address)

			if extension == ".png":
				ResizeImage(address, newResolutions)
			elif extension == ".mp4":
				ResizeVideo(address, newResolutions)

		else:
			files = os.listdir(address)
			ResizeFolder(address, files, newResolutions)

	return


if __name__ == "__main__":

	print("agrs: " + str(sys.argv))

	path = sys.argv[1]

	print("path: " + path)
	files = os.listdir(path)

	newResolutions = [(1920, 1080), (960, 540), (480, 270)]
	print("newResolution: " + str(newResolutions))
	ResizeFolder(path, files, newResolutions)