# Creates the new version of DATA0.DAT and
# Remember to add the original shift_jis bytes you replaced to the format_utils.py script


from PIL import Image
import os
import numpy as np
import cv2

BRUSH_SIZE = 1   # in glyph pixels
DRAW_VALUE = 255
ERASE_VALUE = 0
ZOOM = 20

NEW_GLYPHS_FOLDER = "my_glyphs"
INPUT_FILE = "DATA0.DAT"


WIDTH = 22
HEIGHT = 22
GLYPH_SIZE = WIDTH * HEIGHT
START_OFFSET_1 = 0x7fd4 - 22
START_OFFSET_2 = 0x399000 + 0x2fd4 - 22


def read_image_as_bytes(path):
	img = Image.open(path).convert("L")
	if img.size != (WIDTH, HEIGHT):
		raise ValueError(f"{path} must be {WIDTH}x{HEIGHT}, got {img.size}")

	arr = np.array(img, dtype=np.uint8)
	return arr.flatten().tobytes()

with open(INPUT_FILE, "r+b") as inputFile:
	data = bytearray(inputFile.read())


for filename in os.listdir(NEW_GLYPHS_FOLDER):
	if not filename.lower().endswith((".png", ".bmp", ".jpg")):
		continue

	name = os.path.splitext(filename)[0]
	try:
		idx = int(name)
	except:
		print(f"Skipping {filename} (not numeric)")
		continue

	image_path = os.path.join(NEW_GLYPHS_FOLDER, filename)
	image_bytes = read_image_as_bytes(image_path)

	start = START_OFFSET_1 + idx * GLYPH_SIZE
	end = start + HEIGHT * WIDTH
	data[start:end] = image_bytes

	start = START_OFFSET_2 + idx * GLYPH_SIZE
	end = start + HEIGHT * WIDTH
	data[start:end] = image_bytes


with open(os.path.join(NEW_GLYPHS_FOLDER, INPUT_FILE), "wb") as file:
	file.write(data)