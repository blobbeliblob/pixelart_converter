'''
author: Camilo Hernández

This script takes a video file and converts it into pixelart based on the given initial parameters

file_name	# this should point to the name of the image file (without the file extension)
file_format	# this should be the type of file
new_file_appendix	# this should be what is added to the file name on the new image
pixel_size	# this should be the size of a square in the pixelart, i.e. how many pixels wide and high it is
color_palette_src	# this should point to a file containing data on the colors used in the pixelart image
fps	# this should be the number of frames per second

'''

from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips

#returns color closest to the given color using Euclidean distance
def pixel_color(pixel, palette):
	closest_color = palette[0]
	minimum_distance = (closest_color[0]-pixel[0])**2+(closest_color[1]-pixel[1])**2+(closest_color[2]-pixel[2])**2
	for color in palette:	#color[0]=R, color[1]=G, color[2]=B
		distance = (color[0]-pixel[0])**2+(color[1]-pixel[1])**2+(color[2]-pixel[2])**2
		if distance < minimum_distance:
			minimum_distance = distance
			closest_color = color
	return closest_color

#converts the given video into pixelart
def pixelart(vid, size, color_palette_src, fps,fast=True):
	duration = vid.duration	#duration
	if fps == "default":
		fps = vid.fps	#framerate
	frames = []
	for frame in vid.iter_frames():
		frames.append(frame)
	#get the color palette
	try:
		print("Opening palette...")
		color_file = open(color_palette_src, "r")
		color_data = color_file.readlines()
		palette = []
		for color in color_data:
			c = color.split(",")
			palette.append((int(c[0]), int(c[1]), int(c[2])))
		print("Successful!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e))
		print("Video returned without modification.\n")
		return vid	#return the image non-modified
	width, height = len(frames[0][0]), len(frames[0])	#get dimensions
	width_to_remove = width % size
	height_to_remove = height % size
	#crop the image to fit the pixel size
	print("Cropping image...")
	for i in range(height_to_remove):
		frames[0] = np.delete(frames[0], height - 1 - i, axis=0)
	for i in range(width_to_remove):
		frames[0] = np.delete(frames[0], width - 1 - i, axis=1)
	print("before:\twidth:\t" + str(width) + ", height:\t" + str(height))
	width, height = len(frames[0][0]), len(frames[0])	#get new dimensions
	print("after:\twidth:\t" + str(width) + ", height:\t" + str(height))
	print("Successful!\n")
	print("Processing frames...")
	edited_frames = []
	counter = 0
	for f in frames:
		frame = f.copy()
		if not fast:
			for x in range(width):
				for y in range(height):
					frame[y][x] = pixel_color(frame[y][x], palette)
		for x in range(0, width, size):
			for y in range(0, height, size):
				r, g, b = 0, 0, 0
				for i in range(x, x+size):
					for j in range(y, y+size):
						r, g, b = r + frame[j][i][0], g + frame[j][i][1], b + frame[j][i][2]
				r, g, b = r/(size**2), g/(size**2), b/(size**2)
				color = pixel_color((r, g, b), palette)
				for i in range(x, x+size):
					for j in range(y, y+size):
						frame[j][i] = color
		print("Progress: " + str(counter) + " / " + str(fps * duration), end="\r")
		counter += 1;
		edited_frames.append(frame)
	print("\nFrames processed!\n")
	edited_frames = [ImageClip(frame).set_duration(1/float(fps)) for frame in edited_frames]
	vid = concatenate_videoclips(edited_frames)
	return vid

def main():
	#initial data
	file_name = "test"	#name of the video to be converted
	file_format = "mp4"	#format of the video to be converted
	new_file_appendix = "_pixelart"	#added to the name of the new file, leave as empty string if source file should be replaced
	src = file_name + "." + file_format
	pixel_size = 4	#how many pixels wide and high should a "pixel" be in the new image
	color_palette_src = "palette_32"	#name of the file containing color palette, each color should be on a new line, rgb values should be comma separated, no whitespace
	fps = "default"	#frames per second of the pixelart video, set to "default" for the same as the source video
	#open the video
	try:
		print("Opening video...")
		vid = VideoFileClip(src)
		duration = vid.duration	#duration
		if fps == "default":
			fps = vid.fps	#framerate
		print("Successful!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e) + "\n")
		print("Program will terminate.")
		return	#end the program
	#process the frames
	try:
		print("Converting...\n")
		vid = pixelart(vid, pixel_size, color_palette_src, fps)
		print("Conversion successful!\n")
	except Exception as e:
		print("Conversion failed!")
		print("Error: " + str(e) + "\n")
	#save the video
	try:
		print("Saving video...")
		new_src = file_name + new_file_appendix + "." + file_format
		vid.write_videofile(new_src, fps=fps)
		print("Successful!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e) + "\n")
		print("Program will terminate.")
		return	#end the program

main()

#end of program
