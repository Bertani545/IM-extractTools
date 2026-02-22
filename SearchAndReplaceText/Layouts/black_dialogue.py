import tkinter as tk
from tkinter import filedialog
import sys
import re
import json
import format_utils as FU
from . import info
import data as dialoge_info


CURRENT_SEARCH = ""
SEACRH_OFFSET = 0
INITIAL_CHAR = '\0' # For some cases
END_CHAR = '\0'
LINE_SIZE = dialoge_info.black_dialogues['line_size']

def on_modified(event, ver, newText, sizeLimit, data):
	text = newText[ver].get("1.0", "end-1c")
	edited_text = FU.complyLineSize(text, LINE_SIZE)
	if edited_text != text:
		newText[ver].edit_modified(False)
		newText[ver].delete("1.0", "end")
		newText[ver].insert("1.0", edited_text)
		text = edited_text

	total = FU.getTextSize(text)
	data.current_size[ver] = total
	sizeLimit[ver].config(text=f"{data.current_size[ver]}/{data.size}")
	newText[ver].edit_modified(False)


class Data:

	def __init__(self, newText):
		self.size = 0
		self.offset = 0
		self.current_size = {}
		self.og_dialogue = ''
		self.new_dialogue = newText

	def add(self, textDada):
		to_save = {
			"type": 1,
			"offset": self.offset,
			"size": self.size,
			"original": self.og_dialogue,
		}
		for key, value in self.new_dialogue.items():
			#print(value)
			to_save[key] = value.get("1.0", "end-1c")
		

		textDada[str(self.offset)] = to_save


	
	



#file is an open json file
def saveJSON(file, newText, oldText, text_data):
	offset = text_data['offset']
	n_bytes = text_data['size']
	keys = newText.keys()

	for key in keys:
		text = newText[key].get("1.0", "end-1c")
		line_result = FU.checkLines(text, LINE_SIZE)
		if (line_result != -1):
			tk.messagebox.showinfo("Warning", f"Line {line_result + 1} is bigger than the limit {LINE_SIZE} characters")
			return 
		formated = FU.formatText(text)
		pad_len = n_bytes - len(formated)
		if (pad_len < 0):
			tk.messagebox.showinfo("Warning", 'Too Big! Cannot save that')
			return
	file.seek(0)
	try:
		data = json.load(file)
	except json.JSONDecodeError:
		data = {}
	if str(offset) not in data:
		data[str(offset)] = {
			"size": n_bytes,
			"original": oldText.get("1.0", "end-1c")
		}
	for key in keys:
		text = newText[key].get("1.0", "end-1c")
		data[str(offset)][key] = text

	file.seek(0)
	file.truncate()
	json.dump(data, file, ensure_ascii=False, indent=4)

	file.flush()
	tk.messagebox.showinfo("Info", 'Saved! :)')


def closeGUI(tkinterStuff, text_data):
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	sizeLimit = tkinterStuff['limit']

	textToMod.config(state="normal")
	textToMod.delete('1.0', tk.END)
	for _, nt in newText.items():
		nt.delete('1.0', tk.END)
	text_data.size = 0
	text_data.offset = 0
	for lang in info.languages:
			text_data.current_size[lang] = 0
	return "Try Again"

def finishTranslationSetup(binary_data, text_map, tkinterStuff, text_data, offset):
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	sizeLimit = tkinterStuff['limit']

	textToMod.config(state="normal")
	textToMod.delete("1.0", "end") 

	i = 0
	byte_data = bytearray()
	while True:
		byte = bytes([binary_data[offset + i]])
		byte_data += byte
		i+=1
		if not byte or byte == b'\x00':  # Stop if we hit the null byte or end of file
			break
	n_bytes = len(byte_data) - 1 # The \0 char
	decoded_text = FU.decodeGameText(byte_data)

	text_data.original = decoded_text

	textToMod.insert("1.0", decoded_text)
	textToMod.grid()
	for _, nt in newText.items():
		# TODO: Clean it or search in the json fot the last one
		nt.delete('1.0', tk.END)
		nt.grid()
	text_data.size = n_bytes


	text_data.offset = offset
	res = f"Found at offset {offset:#x}"

	# Write if old data is found
	key = str(offset)
	if key in text_map:
		for lang in info.languages:
			try:
				text = text_map[key][lang]
			except:
				text = ""
			newText[lang].insert("1.0", text)
			text_data.current_size[lang] = FU.getTextSize(text)
	else:
		for lang in info.languages:
			text_data.current_size[lang] = 0
		for _, lim in sizeLimit.items():
			lim.config(text=f"0/{n_bytes}")
	return res

	
	return res

def startNewTranslationOffset(binary_data, text_map, tkinterStuff, text_data):
	offset = tkinterStuff['inputOffset'].get("1.0", "end-1c")
	pos = 0
	if len(offset) > 2 and offset[0:2] == '0x': # Hex
		try:
			pos = int(offset, 16)
		except:
			pos = -1
	else: # hopefully decimal
		try:
			pos = int(offset, 10)
		except:
			pos = -1
	if offset == "" or pos == -1:
		return

	if pos >= 0:
		res = finishTranslationSetup(binary_data, text_map, tkinterStuff, text_data, pos)
	else:
		res = closeGUI(tkinterStuff, text_data)

	tkinterStuff['offset'].configure(text = res)
	tkinterStuff['allText'].config(state="disabled")


def startNewTranslationText(binary_data, text_map, tkinterStuff, text_data, start_sym='', end_sym=''):
	global SEACRH_OFFSET
	global CURRENT_SEARCH

	inputText = tkinterStuff['inputText']
	text = inputText.get("1.0", "end-1c") #Removes last \n

	if text != CURRENT_SEARCH:
		SEACRH_OFFSET = 0
		CURRENT_SEARCH = ""

	if text == "":
		return 
	encoded = FU.prepareTextForSearch(text, start_sym, end_sym)

	pos = binary_data.find(encoded, SEACRH_OFFSET)

	if pos >= 0:
		SEACRH_OFFSET = pos + 1
		CURRENT_SEARCH = text

		if start_sym != '':
			pos += 1 # We don't care about this one
		if end_sym != '':
			pos = binary_data.rfind(bytes([INITIAL_CHAR]), 0, pos) + 1
		res = finishTranslationSetup(binary_data, text_map, tkinterStuff, text_data, pos)
	else:
		tk.messagebox.showinfo("Info", 'Restarting')
		res = closeGUI(tkinterStuff, text_data)
		SEACRH_OFFSET = 0

	tkinterStuff['offset'].configure(text = res)
	tkinterStuff['allText'].config(state="disabled")


def create_layout(root, binary_data, text_data):
	frame = tk.Frame(root)

	lbl = tk.Label(frame, text = "Input text to find")
	lbl.grid(column=0, row=0)

	iptText = tk.Text(frame, width=50, height=5)
	iptText.config(state="normal")
	iptText.grid(column=0, row=1)

	lblOffsetIn = tk.Label(frame, text = "Input offset to follow")
	lblOffsetIn.grid(column = 1, row = 0)

	iptOffset = tk.Text(frame, width=50, height=1)
	iptOffset.config(state="normal")
	iptOffset.grid(column=1, row=1)


	# Info
	offsetlbl = tk.Label(frame, text = "")
	offsetlbl.grid(column=0, row=3)

	# ----
	textToMod = tk.Text(frame, width=50, height=20, font=("Arial", 12))
	textToMod.grid(column=0, row=4)
	textToMod.config(state="disabled")

	# ---- Output
	sizeLimit = {}
	newText = {}
	currCol = 1
	for lang in info.languages:
		#print(info.languages)
		sL = tk.Label(frame, text = "Total: 0/0")
		sL.grid(column=currCol, row = 5)
		sizeLimit[lang] = sL

		try:
			label = tk.Label(frame, text = info.FullLangName[lang])
		except:
			label = tk.Label(frame, text = "I'm a default text")
		label.grid(column=currCol, row=3)
		
		nT = tk.Text(frame, width=50, height=20, font=("Arial", 12))
		nT.config(state="normal")
		nT.grid(column=currCol, row=4)
		newText[lang] = nT

		currCol += 1
	
	


	toBeMod = {'inputText':iptText, 'inputOffset':iptOffset,
				'offset':offsetlbl,  'allText':textToMod, 'newText': newText, 
				'limit': sizeLimit}
	
	# To update while we write
	
	for lang in info.languages:
		nT = newText[lang]
		# We have to pass the value to the lambda fucntion
		nT.bind("<<Modified>>", lambda event, lang=lang: on_modified(event, lang, newText, sizeLimit, data))
		nT.grid_remove()

	textToMod.grid_remove()

	btn_frame = tk.Frame(frame)
	searchBtnFullText = tk.Button(btn_frame, text = "Find as whole" ,
				 fg = "red", command=lambda:startNewTranslationText(binary_data, text_data, toBeMod, data, INITIAL_CHAR, END_CHAR))
	searchBtnStartText = tk.Button(btn_frame, text = "Find as start" ,
				 fg = "red", command=lambda:startNewTranslationText(binary_data, text_data, toBeMod, data, INITIAL_CHAR, ''))
	searchBtnEndText = tk.Button(btn_frame, text = "Find as end" ,
				 fg = "red", command=lambda:startNewTranslationText(binary_data, text_data, toBeMod, data, '', END_CHAR))
	
	data = Data(newText)

	searchBtnOffset = tk.Button(frame, text = "Go to Offset" ,
				 fg = "red", command=lambda:startNewTranslationOffset(binary_data, text_data, toBeMod, data))

	# set Button grid
	#, bg="lightblue", width=200, height=100, bd=3, relief=tk.RIDGE)
	
	btn_frame.grid(column=0, row=2)
	searchBtnFullText.grid(in_=btn_frame, column=0, row=0)
	searchBtnStartText.grid(in_=btn_frame, column=1, row=0)
	searchBtnEndText.grid(in_=btn_frame, column=2, row=0)
	searchBtnOffset.grid(column=1, row=2)

	tk.Label(frame,  text = f"Remeber that the line limit is {LINE_SIZE} chars").grid(column=1, row=7)

	
	return frame, data
		
