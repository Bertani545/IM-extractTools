import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import sys
import re
import json
import format_utils as FU
import Layouts as layouts

text_types = ["Regular", "Black", "Options", "Item description", "Letter", "Phone call"]
display_functions = [
	layouts.normal_dialogue.create_layout,
	layouts.black_dialogue.create_layout
]

ADD_TRANSLATION = False
def saveJSON(json_path, textData):
	if ADD_TRANSLATION:
		ADD_TRANSLATION(textData)
	json_data = {}
	json_data["languages"] = layouts.info.languages
	json_data["data"] = textData
	with open(json_path, "w") as file:
		#print(json_data)
		file.seek(0)
		json.dump(json_data, file, ensure_ascii=False, indent=4)
		file.flush()
		tk.messagebox.showinfo("Info", 'Saved! :)')

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  


def create_display(Id, root, binary_data, text_data):
	if Id == -1:
		return False
	return display_functions[Id](root, binary_data, text_data)

CURRENT_DISPLAY = False
def textType_changed(event, root, binary_data, text_data ):
	global CURRENT_DISPLAY
	global ADD_TRANSLATION
	if CURRENT_DISPLAY:
		CURRENT_DISPLAY.grid_remove()

	selected_value= event.widget.get()
	CURRENT_DISPLAY, class_data  = create_display(text_types.index(selected_value), root, binary_data, text_data)
	CURRENT_DISPLAY.grid(column=0, row=1)
	ADD_TRANSLATION = class_data.add


if __name__ == '__main__':

	binary_path = sys.argv[1] #Path to SLPS_255.47 to modify
	json_path = sys.argv[2]

	with open(binary_path, "r+b") as binaryFile:
		binaryData = binaryFile.read() # Inmutable

	with open(json_path, 'r', encoding="utf8") as jsonFile:
		jsonFile.seek(0)
		try:
			jsonData = json.load(jsonFile)
		except json.JSONDecodeError:
			jsonData = {}
		try:
			textData = jsonData["data"]
		except:
			textData = {}



	root = tk.Tk()

	root.title("Modify text in the game")
	root.geometry('1800x800')
	tk.Button(root, font=("Arial", 12, "bold"), text="Copy …", command=lambda: copy_to_clipboard("…")).grid(column=1, row=0)
		
		
	dropdown = ttk.Combobox(root, values=text_types, state="readonly")
	dropdown.grid(column=0, row=0)
	dropdown.bind("<<ComboboxSelected>>", lambda event:textType_changed(event, root, binaryData, textData))

	saveButton = tk.Button(root, text = "Save to JSON" ,
							fg = "red", command=lambda:saveJSON(json_path, textData))
	saveButton.grid(column=0, row=2)

	# Let's add the flags
	tk.Label(root, justify="left", text = "Flags we may encounter:\nB->0xA1    C->C          D->0xA2\nF->0xA3    G->0xA4    I->I    \nJ->0xA5     K->0xA6    O->0xA7\nP->0xA8    Q->0xA9    R->0xAA\nS->0xAB    T->0xAC    W->W").grid(column=1, row=2)

	root.mainloop()
		
