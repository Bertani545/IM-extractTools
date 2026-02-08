import tkinter as tk
from tkinter import filedialog
import sys
import re
import json
import format_utils as FU


# For any number of languages
languages = {'en', 'es'}
FullLangName = {'en': 'English Version', 'es': 'Versión en Español'}

CURRENT_SEARCH = ""
SEACRH_OFFSET = 0

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  

def on_modified(event, ver, newText, sizeLimit, data):
    text = newText[ver].get("1.0", "end-1c")
    edited_text = FU.complyLineSize(text)
    if edited_text != text:
        newText[ver].edit_modified(False)
        newText[ver].delete("1.0", "end")
        newText[ver].insert("1.0", edited_text)
        text = edited_text

    total = FU.getTextSize(text)
    data['current_size'][ver] = total
    sizeLimit[ver].config(text=f"{data['current_size'][ver]}/{data['size']}")
    newText[ver].edit_modified(False)




'''
offset {
	'size': n
	'original': ~~ 
	'key1': ~~
	'key2': ~~
}
'''
#file is an open json file
def saveJSON(file, newText, oldText, text_data):
	offset = text_data['offset']
	n_bytes = text_data['size']
	keys = newText.keys()

	for key in keys:
		text = newText[key].get("1.0", "end-1c")
		line_result = FU.checkLines(text)
		if (line_result != -1):
			tk.messagebox.showinfo("Warning", f"Line {line_result + 1} is bigger than the limit {FU.LINE_SIZE} characters")
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

def finishTranslationSetup(binaryFile, jsonFile, tkinterStuff, text_data, offset):
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	saveButton = tkinterStuff['saveButton']
	sizeLimit = tkinterStuff['limit']

	textToMod.config(state="normal")
	textToMod.delete("1.0", "end") 

	byte_data = bytearray()


	binaryFile.seek(offset)
	while True:
	    byte = binaryFile.read(1)
	    if not byte or byte == b'\x00':  # Stop if we hit the null byte or end of file
	        break
	    byte_data += byte
	n_bytes = len(byte_data)
	decoded_text = FU.decodeGameText(byte_data)


	textToMod.insert("1.0", decoded_text)
	textToMod.grid()
	for _, nt in newText.items():
		# TODO: Clean it or search in the json fot the last one
		nt.delete('1.0', tk.END)
		nt.grid()
	saveButton.grid()
	text_data['size'] = n_bytes
	text_data['offset'] = offset
	res = f"Found at offset {offset:#x}"

	# Write if old data is found
	key = str(offset)
	jsonFile.seek(0)
	try:
		jsonData = json.load(jsonFile)
	except json.JSONDecodeError:
		jsonData = {}
	if key in jsonData:
		for lang in languages:
			try:
				text = jsonData[key][lang]
			except:
				text = ""
			newText[lang].insert("1.0", text)
			text_data['current_size'][lang] = FU.getTextSize(text)
	else:
		for lang in languages:
			text_data['current_size'][lang] = 0
		for _, lim in sizeLimit.items():
			lim.config(text=f"0/{n_bytes}")
	return res

def closeGUI(tkinterStuff, text_data):
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	saveButton = tkinterStuff['saveButton']
	sizeLimit = tkinterStuff['limit']

	textToMod.config(state="normal")
	textToMod.delete('1.0', tk.END)
	for _, nt in newText.items():
		nt.delete('1.0', tk.END)
	saveButton.grid_remove()
	text_data['size'] = 0
	text_data['offset'] = 0
	for lang in languages:
			text_data['current_size'][lang] = 0
	return "Try Again"

def startNewTranslationOffset(binaryFile, jsonFile, tkinterStuff, text_data):
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
		res = finishTranslationSetup(binaryFile, jsonFile, tkinterStuff, text_data, pos)
	else:
		res = closeGUI(tkinterStuff, text_data)

	tkinterStuff['offset'].configure(text = res)
	tkinterStuff['allText'].config(state="disabled")
	binaryFile.seek(0)


def startNewTranslationText(binaryFile, jsonFile, tkinterStuff, text_data, start_sym='', end_sym=''):
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
	data = binaryFile.read()

	pos = data.find(encoded, SEACRH_OFFSET)

	if pos >= 0:
		SEACRH_OFFSET = pos + 1
		CURRENT_SEARCH = text

		if start_sym != '':
			pos += 1 # We don't care about this one
		if end_sym != '':
			pos = data.rfind(b']', 0, pos) + 1

		res = finishTranslationSetup(binaryFile, jsonFile, tkinterStuff, text_data, pos)
		
	else:
		tk.messagebox.showinfo("Info", 'Restarting')
		res = closeGUI(tkinterStuff, text_data)
		SEACRH_OFFSET = 0

	tkinterStuff['offset'].configure(text = res)
	tkinterStuff['allText'].config(state="disabled")
	binaryFile.seek(0)

if __name__ == '__main__':

	binary_path = sys.argv[1] #Path to SLPS_255.47 to modify
	json_path = sys.argv[2]
	with open(binary_path, "r+b") as binaryFile, open(json_path, 'a+', encoding="utf8") as jsonFile:
		root = tk.Tk()

		root.title("Modify text in the game")
		root.geometry('1800x800')

		# Search stuff
		lbl = tk.Label(root, text = "Input text to find")
		lbl.grid(column=0, row=0)

		iptText = tk.Text(root, width=50, height=5)
		iptText.config(state="normal")
		iptText.grid(column=0, row=1)


		lblOffsetIn = tk.Label(root, text = "Input offset to follow")
		lblOffsetIn.grid(column = 1, row = 0)
		iptOffset = tk.Text(root, width=50, height=1)
		iptOffset.config(state="normal")
		iptOffset.grid(column=1, row=1)


		# Info
		offsetlbl = tk.Label(root, text = "")
		offsetlbl.grid(column=0, row=3)

		# ----
		textToMod = tk.Text(root, width=50, height=20, font=("Arial", 12))
		textToMod.grid(column=0, row=4)
		textToMod.config(state="disabled")

		# ---- Output
		sizeLimit = {}
		newText = {}
		currCol = 1
		for lang in languages:
			sL = tk.Label(root, text = "Total: 0/0")
			sL.grid(column=currCol, row = 5)
			sizeLimit[lang] = sL

			try:
				label = tk.Label(root, text = FullLangName[lang])
			except:
				label = tk.Label(root, text = "I'm a default text")
			label.grid(column=currCol, row=3)
			
			nT = tk.Text(root, width=50, height=20, font=("Arial", 12))
			nT.config(state="normal")
			nT.grid(column=currCol, row=4)
			newText[lang] = nT

			currCol += 1
		
		data = {'size': 0, 'offset': 0, 'current_size': {'es':0, 'en':0}}

		saveButton = tk.Button(root, text = "Save to JSON" ,
								fg = "red", command=lambda:saveJSON(jsonFile, newText, textToMod, data))
		saveButton.grid(column=1, row=6)

		toBeMod = {'inputText':iptText, 'inputOffset':iptOffset,
					'offset':offsetlbl,  'allText':textToMod, 'newText': newText, 
					'saveButton': saveButton, 'limit': sizeLimit}
		
		# To update while we write
		
		for lang in languages:
			nT = newText[lang]
			# We have to pass the value to the lambda fucntion
			nT.bind("<<Modified>>", lambda event, lang=lang: on_modified(event, lang, newText, sizeLimit, data))
			nT.grid_remove()

		textToMod.grid_remove()
		saveButton.grid_remove()

		btn_frame = tk.Frame(root)
		searchBtnText = tk.Button(btn_frame, text = "Find" ,
		             fg = "red", command=lambda:startNewTranslationText(binaryFile, jsonFile, toBeMod, data))
		searchBtnFullText = tk.Button(btn_frame, text = "Find as whole" ,
		             fg = "red", command=lambda:startNewTranslationText(binaryFile, jsonFile, toBeMod, data, FU.INITIAL_CHAR, FU.END_CHAR))
		searchBtnStartText = tk.Button(btn_frame, text = "Find as start" ,
		             fg = "red", command=lambda:startNewTranslationText(binaryFile, jsonFile, toBeMod, data, FU.INITIAL_CHAR))
		searchBtnEndText = tk.Button(btn_frame, text = "Find as end" ,
		             fg = "red", command=lambda:startNewTranslationText(binaryFile, jsonFile, toBeMod, data, '', FU.END_CHAR))
		


		searchBtnOffset = tk.Button(root, text = "Go to Offset" ,
		             fg = "red", command=lambda:startNewTranslationOffset(binaryFile, jsonFile, toBeMod, data))

		# set Button grid
		#, bg="lightblue", width=200, height=100, bd=3, relief=tk.RIDGE)
		
		btn_frame.grid(column=0, row=2)
		searchBtnText.grid(in_=btn_frame, column=0, row=0)
		searchBtnFullText.grid(in_=btn_frame, column=1, row=0)
		searchBtnStartText.grid(in_=btn_frame, column=2, row=0)
		searchBtnEndText.grid(in_=btn_frame, column=3, row=0)
		searchBtnOffset.grid(column=1, row=2)

		tk.Label(root,  text = "Remeber that the line limit is 28 chars").grid(column=1, row=7)

		# Button for ... in a single char
		btn = tk.Button(root, font=("Arial", 12, "bold"), text="Copy …", command=lambda: copy_to_clipboard("…")).grid(column=3, row=0)

		# Let's add the flags
		tk.Label(root, justify="left", text = "Flags we may encounter:\nB->0xA1    C->C          D->0xA2\nF->0xA3    G->0xA4    I->I    \nJ->0xA5     K->0xA6    O->0xA7\nP->0xA8    Q->0xA9    R->0xAA\nS->0xAB    T->0xAC    W->W").grid(column=0, row=7)

		root.mainloop()
		
