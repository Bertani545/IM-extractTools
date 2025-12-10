import struct
from PIL import Image
import numpy as np
import os


def slice_width(data, slice_width=256):
	h,w,c = data.shape
	assert h == 32, "Different height"

	num_slices = (w + slice_width-1) // slice_width

	slices = []
	for i in range(num_slices):
		start = i  * slice_width
		end = start + slice_width

		chunk = data[:, start:end]

		if chunk.shape[1] < slice_width:
			raise ValueError("Transformation does not fill image with width 256")

		slices.append(chunk)

	output = np.vstack(slices)

	return output


def segments_to_row(img, segment_heigth=32):
	arr = np.array(img)

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


	





def encode_image(img):
	one_row = segments_to_row(img)
	as_seen_in_file = slice_width(one_row)
	raw_data = as_seen_in_file.reshape(-1, 4)
	raw_data = raw_data[:, [3,0,1,2]]
	return raw_data


def save_single_image(file_path, img, offset):
	with open(file_path, "r+b") as file:
		file.seek(offset)
		to_save = encode_image(img)
		file.write(to_save.tobytes())


if __name__ == '__main__':
	img = Image.open("./decoded.png").convert("RGBA")
	output = encode_image(img)
	to_img = output.reshape(-1,256,4)
	new_img = Image.fromarray(to_img.astype(np.uint8), "RGBA")

	new_img.save("encoded.png")

	# Saves to the first picture in DATA1.DAT
	save_single_image("../DATA1.DAT", img, 16384 + 0x200 - 0x1)


