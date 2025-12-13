import struct
from PIL import Image
import numpy as np
import os
import json
import shutil

target_hex = "400000000fc5bd43"
target_bytes = bytes.fromhex(target_hex)
PIXEL_SIZE = 4  # RGBA


def to_og_shape(data, og_height, og_width, offset=0):
	h,w,c = data.shape
	assert h == 32, "Different height"

	num_slices = og_height // h

	slices = []
	for i in range(num_slices):
		start = offset + i  * og_width
		end = start + og_width
		chunk = data[:, start:end]

		if chunk.shape[1] < og_width:
			raise ValueError("Transformation does not fill image with width 256")

		slices.append(chunk)

	output = np.vstack(slices)

	return output, og_width * num_slices


def segments_to_row(img, segment_heigth=32):
	arr = img

	h,w,c = arr.shape

	num_segments = (h + segment_heigth - 1) // segment_heigth

	segments = []

	for i in range(num_segments):
		start = i * segment_heigth
		end = start + segment_heigth

		segment = arr[start:end]

		if segment.shape[0] < segment_heigth:
			pad_amount = segment_heigth - segment.shape[0]
			pad = np.zeros((pad_amount, w, c), dtype=arr.dtype)
			segment = np.vstack([segment, pad])

		segments.append(segment)

	output = np.hstack(segments)
	return output


def decode(img, h, w):
	one_row = segments_to_row(img)
	reshaped = to_og_shape(one_row, h, w)
	return reshaped

def decode_multiple(images, sizes):
	one_row = segments_to_row(images)
	return one_row
	offset = 0
	images = []
	for h,w in sizes:
		print(":)")
		reshaped, advanced = to_og_shape(one_row, h, w, offset)
		offset += advanced
		images.append(reshaped)
	return images

def extract_img(data, base_offset, height, width):
	start = base_offset
	end = base_offset + height * width * PIXEL_SIZE
	img = np.frombuffer(data[start:end], dtype=np.uint8)
	img = img.reshape(-1, 4)
	rgba = img[:, [1,2,3,0]].copy()
	rgba[:,3]=255
	h = height * width // 256
	img = rgba.reshape(h, 256, 4)
	return img

def extract_images(data, base_offset, sizes):
	data_size = 0
	for h,w in sizes:
		data_size += h * w * PIXEL_SIZE

	start = base_offset
	end = base_offset + data_size
	img = np.frombuffer(data[start:end], dtype=np.uint8)
	img = img.reshape(-1, 4)
	rgba = img[:, [1,2,3,0]].copy()
	rgba[:,3]=255
	h = data_size // (256 * 4)
	img = rgba.reshape(h, 256, 4)
	return img


def get_special_number(data, offset):
	return data[offset + 0xD]

def get_header_offset(data, offset):
	special_num = get_special_number(data, offset)
	return special_num * 0x100 -0x1

def get_n_images(data, offset):
	return data[offset + 0x14]

def get_size(data, offset_of_image):
	size_data = data[offset_of_image + len(target_bytes) : offset_of_image + len(target_bytes) + 4] 
	if (len(size_data) < 4):
			print("Couldn't read size of the image")
			return []
	width = struct.unpack("<H", size_data[0:2])[0]
	height = struct.unpack("<H", size_data[2:4])[0]
	#if (not ((width > 0 and width <= 640) and (height > 0 and height <= 448))):
	#	print("Not an image of this game")#continue
	#	return []
	return height, width

def decode_imageMultiple_in_file(data, offset):
	header_offset = get_header_offset(data, offset)
	base = offset + header_offset
	print(header_offset)
	n_images = get_n_images(data, offset)
	print(n_images)
	if (n_images < 1):
		return []
	sizes = []
	for i in range(n_images):
		h,w = get_size(data, offset + 0x40 * (i + 1))
		print(h,w)
		sizes.append((h,w))
	print(sizes)

	base_offset = offset + header_offset
	all_data = extract_images(data, base_offset, sizes)
	images = decode_multiple(all_data, sizes)
	return [images]


def decode_imageSingle_in_file(data, offset):
	header_offset = get_header_offset(data, offset)
	base = offset + header_offset

	# Obtain size
	size_data = data[offset + 0x40 + len(target_bytes) : offset + 0x40 + len(target_bytes) + 4] 
	if (len(size_data) < 4):
			print("Couldn't read size of the image")
			return
	width = struct.unpack("<H", size_data[0:2])[0]
	height = struct.unpack("<H", size_data[2:4])[0]
	if (not ((width > 0 and width <= 640) and (height > 0 and height <= 448))):
		print("Not an image of this game")#continue
		return

	base_offset = offset + header_offset
	raw_data = extract_img(data, base_offset, height, width)
	decoded = decode(raw_data, height, width)
	return decoded

if __name__ == '__main__':
	with open("../DATA1.DAT", "rb") as f:
		data = f.read()

		idx = data.find(target_bytes, 0)
		if (idx == -1):
			raise ValueError("Bad")
		out_img = decode_imageSingle_in_file(data, idx)

		img = Image.fromarray(out_img, "RGBA")
		img.save("decoded.png")
