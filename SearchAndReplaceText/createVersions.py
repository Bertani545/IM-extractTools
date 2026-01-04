import sys
import json
import os
import shutil
import format_utils as FU



def createNewFiles(json_data, exec_path):
	first_offset = next(iter(json_data))
	block = json_data[first_offset]

	variant_keys = [k for k in block.keys() if k not in ("size", "original")]
	files = {}
	for key in variant_keys:
		os.makedirs(key, exist_ok=True)
		new_exec = os.path.join(key, os.path.basename(exec_path))
		shutil.copyfile(exec_path, new_exec) # Copy
		files[key] = open(new_exec, "r+b")
	for offset_str, entry in json_data.items():
		offset = int(offset_str)
		n_bytes = entry["size"]
		for key in variant_keys:
			text = entry[key]
			formated = FU.formatText(text)
			
			pad_len = n_bytes - len(formated)
			if (pad_len < 0):
				print('Too Big! Cannot write that')
				return

			files[key].seek(offset)
			files[key].write(formated + b"\x20" * pad_len)
			files[key].flush()

	for f in files.values():
		f.close()

if __name__ == '__main__':

	slps_path = sys.argv[1] #Path to SLPS_255.47 to modify
	json_path = sys.argv[2]

	with open(json_path, "r", encoding="utf8") as f:
		data = json.load(f)
		createNewFiles(data, slps_path)