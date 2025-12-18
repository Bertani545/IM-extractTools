import tkinter as tk
from tkinter import filedialog
import sys
import re
import json
import format_utils as FU


# For any number of languages
languages = {'en', 'es'}
FullLangName = {'en': 'English Version', 'es': 'Versión en Español'}



def on_modified(event, ver, newText, sizeLimit, data):
    text = newText[ver].get("1.0", "end-1c")
    total = FU.getTextSize(text)
    data['current_size'][ver] = total
    sizeLimit[ver].config(text=f"{data['current_size'][ver]}/{data['size']}")
    newText[ver].edit_modified(False)

#28 letter per line

def checkLines(text):
	lines = text.split('\n')
	for line in lines:
		clean = re.sub(r"0x.", "", line)
		if len(clean) > 28:
			return False
	return True

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
		if not checkLines(text):
			print(f"A line is not the desired length in {key}")
			return 
		formated = FU.formatText(text)
		pad_len = n_bytes - len(formated)
		if (pad_len < 0):
			print('Too Big! Cannot save that')
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
	print("Saved!")
	'''
	file.seek(offset)
	formated = FU.formatText(text)

	pad_len = n_bytes - len(formated)
	if (pad_len < 0):
		print('Too Big! Cannot write that')
		return

	file.write(formated + b"\x20" * pad_len)
	file.flush()
	'''

def finishTranslationSetup(binaryFile, jsonFile, tkinterStuff, text_data, offset):
	offsetlbl = tkinterStuff['offset']
	textToMod = tkinterStuff['allText']
	newText = tkinterStuff['newText']
	saveButton = tkinterStuff['saveButton']
	sizeLimit = tkinterStuff['limit']

	textToMod.config(state="normal")
	textToMod.delete("1.0", "end") 

	res = f"Found at offset {offset:#x}"
	binaryFile.seek(offset)
	byte_data = []
	while True:
	    byte = binaryFile.read(1)
	    if not byte or byte == b'\x00':  # Stop if we hit the null byte or end of file
	        break
	    byte_data.append(byte)
	n_bytes = len(byte_data)
	byte_data = b''.join(byte_data)
	decoded_text = byte_data.decode('shift_jis')

	textToMod.insert("1.0", decoded_text)
	textToMod.grid()
	for _, nt in newText.items():
		# TODO: Clean it or search in the json fot the last one
		nt.delete('1.0', tk.END)
		nt.grid()
	saveButton.grid()

	text_data['size'] = n_bytes
	text_data['offset'] = offset

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
	try:
		pos = int(offset)
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

def startNewTranslationText(binaryFile, jsonFile, tkinterStuff, text_data):

	inputText = tkinterStuff['inputText']
	text = inputText.get("1.0", "end-1c") #Removes last \n
	if text == "":
		return 
	encoded = text.encode("shift_jis")
	data = binaryFile.read()
	pos = data.find(encoded)

	if pos >= 0:
		res = finishTranslationSetup(binaryFile, jsonFile, tkinterStuff, text_data, pos)
	else:
		res = closeGUI(tkinterStuff, text_data)

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
		textToMod = tk.Text(root)
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
			
			nT = tk.Text(root, width=50, height=25)
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
		searchBtnText = tk.Button(root, text = "Find first occur" ,
		             fg = "red", command=lambda:startNewTranslationText(binaryFile, jsonFile, toBeMod, data))
		searchBtnOffset = tk.Button(root, text = "Go to Offset" ,
		             fg = "red", command=lambda:startNewTranslationOffset(binaryFile, jsonFile, toBeMod, data))

		# set Button grid
		searchBtnText.grid(column=0, row=2)
		searchBtnOffset.grid(column=1, row=2)

		tk.Label(root, text = "Remeber that th line limit is 28 chars").grid(column=1, row=7)

		root.mainloop()


