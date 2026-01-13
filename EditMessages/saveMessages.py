import struct
from PIL import Image
import numpy as np
import os
import json
import shutil

# Expected to be outside the folder messages and executed after you finished your translations
# Data0 is in the same folder

'''
Folder structure example:
	saveMessages.py
	DATA0.DAT
	messages/
		og_images
		offsets.json
		en/
			new_images.png
		es/
			new_images.png
'''

LANGUAGES = ["en", "es"]
BASE_FILE = "DATA0.DAT"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
offset_data = os.path.join(SCRIPT_DIR, "messages", "offsets.json")
data_path = os.path.join(SCRIPT_DIR, BASE_FILE)


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

	output = slice_width(output)
	h,w,c = output.shape
	alpha = np.full((h,w,1), 0x80, dtype=np.uint8)

	rgba = np.concatenate([output.astype(np.uint8), alpha], axis=2)


	#new_img = Image.fromarray(rgba.astype(np.uint8), "RGBA")
	return rgba


	# Finally
	output = output.reshape(-1, 3)

def save_img(img, where_path, offset):
	with open(where_path, "r+b") as DATA0:		
		img = img.reshape(-1, 4)
		abgr = img[:, [3,2,1,0]]

		DATA0.seek(offset)
		DATA0.write(abgr.tobytes())


if __name__ == '__main__':
	with open(offset_data, 'r', encoding="utf8") as f:
		json_data = json.load(f)
		for lang in LANGUAGES:
			lang_dir = os.path.join(SCRIPT_DIR, "messages", lang)
			if not os.path.isdir(lang_dir):
				continue

			patched_path = os.path.join(lang_dir, BASE_FILE)
			shutil.copyfile(data_path, patched_path)
			for message_id, offset in json_data.items():
				img_path = os.path.join(lang_dir, f"{int(message_id):02d}.png")
				if not os.path.isfile(img_path):
					continue
				img = Image.open(img_path).convert("RGB")
				coded_img = segments_to_row(img)
				save_img(coded_img, patched_path, offset)
	

	




