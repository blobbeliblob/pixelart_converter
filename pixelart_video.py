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
import numpy as np
import time

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
def pixelart(vid, size, color_palette_src, fps, duration, fast=True):
	number_of_frames = round(vid.fps * vid.duration)
	#number_of_frames = (int(number_of_frames/2000))
	height, width, rgb = vid.get_frame(0).shape
	clips = []
	mew = 100	# memory error workaround
	for fi in range(int(number_of_frames/mew) if number_of_frames%mew==0 else int(number_of_frames/mew)+1):
		frame_step = 1#int(fps)
		frames = np.empty((int(number_of_frames/mew/frame_step), height, width, rgb), dtype=np.uint8)
		try:
			print("Accessing frames...")
			for i in range(fi*mew, fi*mew+mew, frame_step):
				frames[i] = vid.get_frame(i)
				print("Progress: " + str(fi*mew+i+1) + " / " + str(number_of_frames), end="\r")
			print("Successful!\n")
		except Exception as e:
			print("Could not access frames!")
			print("Error: " + str(e) + "\n")
			print("Video returned without modification.\n")
			return (vid, False)	#return the image non-modified
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
			return (vid, False)	#return the image non-modified
		height, width, rgb = frames[0].shape	#get dimensions
		try:
			width_to_remove = width % size
			height_to_remove = height % size
			#crop the image to fit the pixel size
			print("Cropping image...")
			frames = frames[:, :height-height_to_remove, :width-width_to_remove, :]
			print("before:\twidth:\t" + str(width) + ", height:\t" + str(height))
			width, height = len(frames[0][0]), len(frames[0])	#get new dimensions
			print("after:\twidth:\t" + str(width) + ", height:\t" + str(height))
			print("Successful!\n")
		except Exception as e:
			print("Failed!")
			print("Error: " + str(e))
			print("Video returned without modification.\n")
			return (vid, False)	#return the image non-modified
		try:
			print("Processing frames...")
			height, width, rgb = frames[0].shape
			edited_frames = np.empty((int(number_of_frames/mew/frame_step), height, width, rgb), dtype=np.uint8)
			for index in range(len(frames)):
				frame = frames[index].copy()
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
				edited_frames[index] = frame
				print("Progress: " + str(fi*mew+index+1) + " / " + str(number_of_frames), end="\r")
			print("\nFrames processed!\n")
		except Exception as e:
			print("Failed!")
			print("Error: " + str(e))
			print("Video returned without modification.\n")
			return (vid, False)	#return the image non-modified
		try:
			print("Concatenating frames...")
			edited_frames = [ImageClip(frame).set_duration(1/float(fps)) for frame in edited_frames]
			new_clip = concatenate_videoclips(edited_frames)
			new_clip.set_duration(duration)
			print("\nFrames concatenated!\n")
		except Exception as e:
			print("Failed!")
			print("Error: " + str(e))
			print("Video returned without modification.\n")
			return (vid, False)	#return the image non-modified
		clips.append(new_clip)
	try:
		print("Concatenating clips...")
		vid = concatenate_videoclips(clips)
		vid.set_duration(duration)
		#vid.preview()
		print("\Clips concatenated!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e))
		print("Video returned without modification.\n")
		return (vid, False)	#return the image non-modified
	return (vid, True)

def main():
	#initial data
	file_name = "1"	#name of the video to be converted
	file_format = "mp4"	#format of the video to be converted
	new_file_appendix = "_pixelart"	#added to the name of the new file, leave as empty string if source file should be replaced
	src = file_name + "." + file_format
	pixel_size = 64	#how many pixels wide and high should a "pixel" be in the new image
	color_palette_src = "palette_8"	#name of the file containing color palette, each color should be on a new line, rgb values should be comma separated, no whitespace
	fps = "default"	#frames per second of the pixelart video, set to "default" for the same as the source video
	fps = 1
	#open the video
	try:
		print("\nOpening video...")
		vid = VideoFileClip(src)
		audio = vid.audio.copy()	#audio
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
	print("Converting...\n")
	vid, vid_ok = pixelart(vid, pixel_size, color_palette_src, fps, duration)
	#vid = vid.set_audio(audio)
	#save the video
	if vid_ok:
		print("Conversion successful!\n")
		print("\nDoing nothing...")
		time.sleep(5)
		print("Continuing...\n")
		#try:
		print("Saving video...")
		new_src = file_name + new_file_appendix + "." + file_format
		vid.write_videofile(new_src, fps=fps)
		print("Successful!\n")
		#except Exception as e:
		#	print("Failed!")
		#	print("Error: " + str(e) + "\n")
		#	return	#end the program
	else:
		print("Conversion failed!")
	print("\nProgram will terminate.")

main()

#end of program
