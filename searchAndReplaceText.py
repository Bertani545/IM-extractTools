import tkinter as tk
from tkinter import filedialog
import sys
import re


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
	'W': b'\x4b\x04\x1d'
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


def on_modified(event, newText, sizeLimit, data):
    text = newText.get("1.0", "end-1c")
    total = getTextSize(text)
    data['current_size'] = total
    sizeLimit.config(text=f"{data['current_size']}/{data['size']}")
    newText.edit_modified(False)

#28 letter per line

def checkLines(text):
	lines = text.split('\n')
	for line in lines:
		clean = re.sub(r"0x.", "", line)
		if len(clean) > 28:
			return False
	return True

def ovewrite(file, newText, text_data):
	offset = text_data['offset']
	n_bytes = text_data['size']
	text = newText.get("1.0", "end-1c")
	if not checkLines(text):
		print("A line is not the desired length")
		return 

	file.seek(offset)
	formated = format(text)

	pad_len = n_bytes - len(formated)
	if (pad_len < 0):
		print('Too Big! Cannot write that')
		return

	file.write(formated + b"\x20" * pad_len)
	file.flush()


def clicked(file, tkinterStuff, text_data):

	inputText = tkinterStuff['inputText']
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	saveButton = tkinterStuff['saveButton']
	sizeLimit = tkinterStuff['limit']

	text = inputText.get("1.0", "end-1c") #Removes last \n
	encoded = text.encode("shift_jis")
	data = file.read()
	pos = data.find(encoded)

	textToMod.config(state="normal")
	textToMod.delete("1.0", "end") 
	if pos != -1:
		res = f"Found at offset {pos:#x}"
		file.seek(pos)
		byte_data = []
		while True:
		    byte = file.read(1)
		    if not byte or byte == b'\x00':  # Stop if we hit the null byte or end of file
		        break
		    byte_data.append(byte)
		n_bytes = len(byte_data)
		byte_data = b''.join(byte_data)
		decoded_text = byte_data.decode('shift_jis')

		textToMod.insert("1.0", decoded_text)
		textToMod.grid()
		newText.grid()
		saveButton.grid()

		text_data['size'] = n_bytes
		text_data['offset'] = pos
		text_data['current_size'] = 0
		sizeLimit.config(text=f"0/{n_bytes}")
	else:
		res = "Try again"
		textToMod.grid_remove()
		newText.grid_remove()
		saveButton.grid_remove()

	textToMod.config(state="disabled")
	offsetlbl.configure(text = res)
	file.seek(0)

if __name__ == '__main__':

	slps_path = sys.argv[1] #Path to SLPS_255.47 to modify
	with open(slps_path, "r+b") as slps:
		root = tk.Tk()

		root.title("Modify text in the game")
		root.geometry('1500x800')

		lbl = tk.Label(root, text = "Input text to find")
		lbl.grid(column=0, row=0)


		iptText = tk.Text(root, width=50, height=5)
		iptText.config(state="normal")
		iptText.grid(column=0, row=1)

		offsetlbl = tk.Label(root, text = "")
		offsetlbl.grid(column=0, row=3)

		textToMod = tk.Text(root)
		textToMod.grid(column=0, row=4)
		textToMod.config(state="disabled")

		# ---- Output

		sizeLimit = tk.Label(root, text = "Total: 0/0")
		sizeLimit.grid(column=2, row = 3)

		lbl2 = tk.Label(root, text = "Write new stuff")
		lbl2.grid(column=1, row=3)

		newText = tk.Text(root, width=50, height=25)
		newText.config(state="normal")
		newText.grid(column=1, row=4)
		
		
		saveButton = tk.Button(root, text = "Save to file" ,
								fg = "red", command=lambda:ovewrite(slps, newText, data))
		saveButton.grid(column=1, row=5)

		toBeMod = {'inputText':iptText, 'offset':offsetlbl, 
					'allText':textToMod, 'newText': newText, 
					'saveButton': saveButton, 'limit': sizeLimit}
		
		# To update while we write
		data = {'size': 0, 'offset': 0, 'current_size': 0}
		newText.bind("<<Modified>>", lambda event: on_modified(event, newText, sizeLimit, data))


		textToMod.grid_remove()
		newText.grid_remove()
		saveButton.grid_remove()
		btn = tk.Button(root, text = "Find first occur" ,
		             fg = "red", command=lambda:clicked(slps, toBeMod, data))
		# set Button grid
		btn.grid(column=0, row=2)

		tk.Label(root, text = "Remeber that th line limit is 28 chars").grid(column=1, row=7)

		root.mainloop()


