from PIL import Image
import os
import struct
import shutil

'''
	Loops through all the [name].bin files in the directory and searches
	in all the LANGUAGES folders for [name].png to create the different
	versions of BASE_FILE

	Example of directory structure:
	- *.bin
	- DATA0.DAT
	En/
		- *.png
	Esp/
		- *.png

	And then:
	- *.bin
	- DATA0.DAT
	En/
		- DATA0.DAT
		- *.png
	Esp/
		- DATA0.DAT
		- *.png
'''

LANGUAGES = ["En", "Esp"]
BASE_FILE = "DATA0.DAT"
PIXEL_FORMAT = "RGBA"
INT_SIZE = 4
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def read_offsets(bin_path):
	offsets = []

	with open(bin_path, "rb") as f:
		data = f.read()

	count = len(data) // INT_SIZE
	for i in range(count):
		offset = struct.unpack_from(">i", data, i * INT_SIZE)[0]
		offsets.append(offset)

	return offsets


def read_pixels(png_path):
	img = Image.open(png_path).convert(PIXEL_FORMAT)
	return list(img.getdata())


def patch_file(fp, offsets, pixels):
	if len(offsets) != len(pixels):
		raise ValueError("Pixel count does not match offset count")

	for offset, pixel in zip(offsets, pixels):
		if (offset < 0):
			continue
		fp.seek(offset)
		fp.write(bytes(pixel))


def process_language(lang):
	lang_dir = os.path.join(SCRIPT_DIR, lang)
	if not os.path.isdir(lang_dir):
		print(f"Skipping {lang}: folder not found")
		return

	patched_path = os.path.join(lang_dir, BASE_FILE)
	shutil.copyfile(BASE_FILE, patched_path)
	print(f"Created patched file: {patched_path}")

	with open(patched_path, "r+b") as base_fp:
		for filename in os.listdir(SCRIPT_DIR):
			if not filename.endswith(".bin"):
				continue

			bin_path = os.path.join(SCRIPT_DIR, filename)
			png_path = os.path.join(
				lang_dir,
				os.path.splitext(filename)[0] + ".png"
			)
			if not os.path.exists(png_path):
				print(f"  Skipping {filename}: PNG not found")
				continue

			print(f"  Patching using {filename}")

			offsets = read_offsets(bin_path)
			pixels = read_pixels(png_path)
			patch_file(base_fp, offsets, pixels)



def main():
	for lang in LANGUAGES:
		print(f"\nProcessing language: {lang}")
		process_language(lang)

	print("Done.")

if __name__ == "__main__":
	main()