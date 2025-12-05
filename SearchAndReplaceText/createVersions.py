import sys
import re
import json
import os
import shutil

letters = {
	'B': b'\x4b\x04\x08',
	'C': b'\x4b\x04\x09',
	'D': b'\x4b\x04\x0a',
	'F': b'\x4b\x04\x0c',
	'G': b'\x4b\x04\x0d',
	'I': b'\x4b\x04\x0f',
	'J': b'\x4b\x04\x10',
	'K': b'\x4b\x04\x11',
	'O': b'\x4b\x04\x15',
	'P': b'\x4b\x04\x16',
	'Q': b'\x4b\x04\x17',
	'R': b'\x4b\x04\x18',
	'S': b'\x4b\x04\x19',
	'T': b'\x4b\x04\x1a',
	'W': b'\x4b\x04\x1d',
	'ñ': b'#'
}

def get_char_size(ch):
    """Return byte length based on custom letters map or shift_jis encoding."""
    if ch in letters:
        return len(letters[ch])
    else:
        return len(ch.encode("shift_jis", errors="replace"))


def format(text):
	out = bytearray()
	i = 0
	length = len(text)
	while i < length:
		ch = text[i]
		if i+2 < length and text[i:i+2] == "0x":
			flag_char = text[i+2]
			out += flag_char.encode("shift_jis", errors="replace")
			i += 3
			continue
		if ch in letters:
			out += letters[ch]
			i += 1
			continue

		out += ch.encode("shift_jis", errors="replace")
		i += 1
	return bytes(out)

def getTextSize(text):
	formated = format(text)
	return(len(formated))


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
			formated = format(text)
			
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