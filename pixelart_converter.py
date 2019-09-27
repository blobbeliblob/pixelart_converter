'''
author: Camilo Hernández

This script takes an image file and converts it into pixelart based on the given initial parameters

file_name	# this should point to the name of the image file (without the file extension)
file_format	# this should be the type of file
new_file_appendix	# this should be what is added to the file name on the new image
pixel_size	# this should be the size of a square in the pixelart, i.e. how many pixels wide and high it is
color_palette_src	# this should point to a file containing data on the colors used in the pixelart image

'''

import os
import sys
from PIL import Image

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

#converts the given image into pixelart
def pixelart(img, size, color_palette_src, fast=True):
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
		print("Image returned without modification.\n")
		return img	#return the image non-modified
	img = img.convert('RGB')	#convert the image to rgb
	width, height = img.size	#get dimensions
	img = img.crop((0, 0, width - width % size, height - height % size))	#crop the image to fit the pixel size
	width, height = img.size	#get new dimensions
	pixels = img.load()	#get pixels
	print("Processing pixels...")
	if not fast:
		for x in range(width):
			for y in range(height):
				pixels[x, y] = pixel_color(pixels[x, y], palette)
			print("Progress: " + str(x + 1) + " / " + str(width), end="\r")
	for x in range(0, width, size):
		for y in range(0, height, size):
			r, g, b = 0, 0, 0
			for i in range(x, x+size):
				for j in range(y, y+size):
					r, g, b = r + pixels[i, j][0], g + pixels[i, j][1], b + pixels[i, j][2]
			r, g, b = r/(size**2), g/(size**2), b/(size**2)
			color = pixel_color((r, g, b), palette)
			for i in range(x, x+size):
				for j in range(y, y+size):
					pixels[i, j] = color
		print("Progress: " + str(x + 1) + " / " + str(width), end="\r")
	print("Pixels processed!\n")
	return img

def main():
	#initial data
	file_name = "test"	#name of the image to be converted
	file_format = "jpg"	#format of the image to be converted
	new_file_appendix = "_pixelart"	#added to the name of the new file, leave as empty string if source file should be replaced
	src = file_name + "." + file_format
	pixel_size = 8	#how many pixels wide and high should a "pixel" be in the new image
	color_palette_src = "palette_16"	#name of the file containing color palette, each color should be on a new line, rgb values should be comma separated, no whitespace
	#open the image
	try:
		print("Opening image...")
		img = Image.open(src)
		print("Successful!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e) + "\n")
		print("Program will terminate.")
		return	#end the program
	#process the image
	try:
		print("Converting...\n")
		img = pixelart(img, pixel_size, color_palette_src)
		print("Conversion successful!\n")
	except Exception as e:
		print("Conversion failed!")
		print("Error: " + str(e) + "\n")
	#save the image
	try:
		print("Saving image...")
		new_src = file_name + new_file_appendix + "." + file_format
		img.save(new_src)
		print("Successful!\n")
	except Exception as e:
		print("Failed!")
		print("Error: " + str(e) + "\n")
		print("Program will terminate.")
		return	#end the program

main()

#end of program
