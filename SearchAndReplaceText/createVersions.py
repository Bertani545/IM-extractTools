import sys
import json
import os
import shutil
import assembly_utils as utils
import data as dialogues_data
import copy
import format_utils as FU
import re


OG_OFFSET_INSTRUCTIONS = 0x2bc7d0
OFFSET_INSTRUCTIONS = {}
OG_OFFSET_TEXT = 0x3bc7a8
OFFSET_TEXT = {}
DISTANCE_TO_VIRTUAL = 0x1a43a00
# 0.5 Mb for each(?) The code works fine but we have to be careful about
# How the memory is managed
#OFFSET_INSTRUCTIONS = 0x3bc7d0
#OFFSET_TEXT = 0x43C7D0
#DISTANCE_TO_VIRTUAL = 0x1243A00
OG_DISTANCE = 0xfff80


#  Not overwritten
# Start = 0x15dfa00 <--- Dangerous
# End =   0x15ffc00 

#start = 0x178b200
#end = 0x17bb580

#start = 0x1c1d37f
#end = 0x1c3d470

OG_DATA = []
TRANS_DATA = {}
LANGUAGES = []

# These errors will have to have the instructions edited manually
ERRORS_PTR = []
ERRORS_JAL = []
def saveToErrorsPtr(og_address, new_address):
	global ERRORS_PTR
	ERRORS_PTR.append({"og_addr":og_address + DISTANCE_TO_VIRTUAL, "new_addr": new_address + DISTANCE_TO_VIRTUAL});

def saveToErrorsJAL(jal_func, text_address):
	global ERRORS_JAL

	jal_text = jal_func.hex()
	# Find in ghidra the instruction linking to text_addr and replace it with jal_inst
	ERRORS_JAL.append({"jal_inst":jal_text, "og_text_addr": text_address + OG_DISTANCE});


def writeToHex(start, data_to_mod, new_data):
	end = start + len(new_data)
	data_to_mod[start:end] = new_data

def writeText(key, encodedText, address=0):
	global OFFSET_TEXT
	new_addres = 0
	if address != 0:
		start = address
		new_addres = address
	else:
		# Use the global OFFSET
		start = OFFSET_TEXT[key]
		new_addres = OFFSET_TEXT[key]
		OFFSET_TEXT[key] += len(encodedText)
	
	writeToHex(start, TRANS_DATA[key], encodedText)
	return new_addres


def writeTextMultiple(key, og_text, n_lines, metadata=b'\x00'):
	lines = og_text.split('\n')
	groups = [lines[i:i + n_lines] for i in range(0, len(lines), n_lines)]
	addresses = []

	for g in groups:
		text = "\n".join(g)
		encoded = FU.formatText(text)
		if metadata != b'\x00':
			encoded = metadata + encoded
		addr = writeText(key, encoded)
		addresses.append(addr)
	return addresses

def writeNewFunctionDialogue(key, new_addresses, audio_id):
	global OFFSET_INSTRUCTIONS
	function = utils.functionDefinition;

	# First one is girls
	function += utils.createGirlsDialogue(new_addresses[0] + DISTANCE_TO_VIRTUAL, audio_id)
	function += utils.stop_function

	for i in range(1, len(new_addresses)):
		function += utils.createMCDialogue(new_addresses[i] + DISTANCE_TO_VIRTUAL)
		function += utils.stop_function

	function = function[:-len(utils.stop_function)] # So it doesn't stop twice
	function += utils.functionReturn

	writeToHex(OFFSET_INSTRUCTIONS[key], TRANS_DATA[key], function)
	target_addres =  OFFSET_INSTRUCTIONS[key] + DISTANCE_TO_VIRTUAL
	jal = utils.createJalInstruction(target_addres)

	OFFSET_INSTRUCTIONS[key] += len(function)

	return jal


def writeNewFunctionBlack(key, new_addresses):
	global OFFSET_INSTRUCTIONS

	function = utils.functionDefinition;

	for addr in new_addresses:
		function += utils.createBlackDialogue(addr + DISTANCE_TO_VIRTUAL)
		function += utils.stop_function

	function = function[:-len(utils.stop_function)] # So it doesn't stop twice
	function += utils.functionReturn

	writeToHex(OFFSET_INSTRUCTIONS[key], TRANS_DATA[key], function)
	target_addres =  OFFSET_INSTRUCTIONS[key] + DISTANCE_TO_VIRTUAL
	jal = utils.createJalInstruction(target_addres)

	OFFSET_INSTRUCTIONS[key] += len(function)

	return jal


def setMCDialogue(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.normal_dialogues

	# Find the orignal instruction
	og_instruction = utils.createMCDialogue(int(dialogue_json["offset"]) + OG_DISTANCE)
	pos_instruction = OG_DATA.find(og_instruction)
	og_pos = pos_instruction
	
	# PAtch it accordingly
	for key in LANGUAGES:
		pos_instruction = og_pos
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)
		metadata = dialogue_json['metadata'].encode("shift_jis", errors="replace")
		whole_text = metadata + formated_text

		# Normal
		if len(formated_text) <= dialogue_json["size"] and n_lines <= int(info["n_lines"]):
			writeText(key, whole_text, dialogue_json["offset"])
			return


		if n_lines <= int(info["n_lines"]):
			# Write the text to the next avaible space
			new_address = writeText(key, whole_text)
			# We won't be able to change it here
			if pos_instruction == -1: 
				saveToErrorsPtr(dialogue_json["offset"], new_address)
				return
			# Only bigger, change the ptr
			new_inst = utils.createMCDialogue(new_address + DISTANCE_TO_VIRTUAL)


			while pos_instruction != -1: #There might be more that one call to the value
				writeToHex(pos_instruction, TRANS_DATA[key], new_inst)
				pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(new_inst))
			return


		# We have to create a new function
		
		new_addresses = writeTextMultiple(key, text, info["n_lines"], metadata)
		jal = writeNewFunctionDialogue(key, new_addresses, 0)
		
		# We cannot write the jal instruction
		if pos_instruction == -1: 
			saveToErrorsJAL(jal, dialogue_json["offset"])
			return

		whole_replacement = jal + b"\x00" * (len(og_instruction) - len(jal))
		while pos_instruction != -1: #There might be more that one call to the value
			writeToHex(pos_instruction, TRANS_DATA[key], whole_replacement)
			pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(whole_replacement))
			

def setGirlDialogue(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.normal_dialogues

	# Find the orignal instruction
	og_instruction = utils.createGirlsDialogue(int(dialogue_json["offset"]) + OG_DISTANCE)
	pattern = (
			re.escape(og_instruction[:4]) +
			b'.{4}' +
			re.escape(og_instruction[8:])
		)
	match =  re.search(pattern, OG_DATA, flags=re.DOTALL)
	if match:
		pos_instruction = match.start()
	else:
		pos_instruction = -1
	og_pos = pos_instruction

	audio_id = 0
	if pos_instruction != -1:
		val = int.from_bytes(OG_DATA[pos_instruction + 4: pos_instruction + 8], byteorder='little')  # or 'little'
		audio_id = utils.extractValFromLi(val)
	# PAtch it accordingly
	for key in LANGUAGES:
		pos_instruction = og_pos
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)
		metadata = dialogue_json['metadata'].encode("shift_jis", errors="replace")
		whole_text = metadata + formated_text

		# Normal
		if len(formated_text) <= dialogue_json["size"] and n_lines <= int(info["n_lines"]):
			writeText(key, whole_text, dialogue_json["offset"])
			return


		if n_lines <= int(info["n_lines"]):
			# Write the text to the next avaible space
			new_address = writeText(key, whole_text)
			# We won't be able to change it here
			if pos_instruction == -1: 
				saveToErrorsPtr(dialogue_json["offset"], new_address)
				return
			# Only bigger, change the ptr
			new_inst = utils.createGirlsDialogue(new_address + DISTANCE_TO_VIRTUAL, audio_id)
			while pos_instruction != -1: #There might be more that one call to the value
				writeToHex(pos_instruction, TRANS_DATA[key], new_inst)
				pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(new_inst))
			return


		# We have to create a new function
		
		new_addresses = writeTextMultiple(key, text, info["n_lines"], metadata)

		jal = writeNewFunctionDialogue(key, new_addresses, audio_id)
		
		# We cannot write the jal instruction
		if pos_instruction == -1: 
			saveToErrorsJAL(jal, dialogue_json["offset"])
			return

		whole_replacement = jal + b"\x00" * (len(og_instruction) - len(jal))
		while pos_instruction != -1: #There might be more that one call to the value
			writeToHex(pos_instruction, TRANS_DATA[key], whole_replacement)
			pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(whole_replacement))


def setBlackDialogue(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.black_dialogues

	# Find the orignal instruction
	og_instruction = utils.createBlackDialogue(int(dialogue_json["offset"]) + OG_DISTANCE)
	pos_instruction = OG_DATA.find(og_instruction)
	og_pos = pos_instruction

	# PAtch it accordingly
	for key in LANGUAGES:
		pos_instruction = og_pos
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)

		# Normal
		if len(formated_text) <= dialogue_json["size"] and n_lines <= int(info["n_lines"]):
			writeText(key, formated_text, dialogue_json["offset"])
			return

		if n_lines <= int(info["n_lines"]):
			# Write the text to the next avaible space
			new_address = writeText(key, formated_text)
			# We won't be able to change it here
			if pos_instruction == -1: 
				saveToErrorsPtr(dialogue_json["offset"], new_address)
				return
			# Only bigger, change the ptr
			new_inst = utils.createBlackDialogue(new_address + DISTANCE_TO_VIRTUAL)
			while pos_instruction != -1: #There might be more that one call to the value
				writeToHex(pos_instruction, TRANS_DATA[key], new_inst)
				pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(new_inst))
			return


		# We have to create a new function
		new_addresses = writeTextMultiple(key, text, info["n_lines"])
		jal = writeNewFunctionBlack(key, new_addresses)
		
		# We cannot write the jal instruction
		if pos_instruction == -1: 
			saveToErrorsJAL(jal, dialogue_json["offset"])
			return

		whole_replacement = jal + b"\x00" * (len(og_instruction) - len(jal))
		while pos_instruction != -1: #There might be more that one call to the value
			writeToHex(pos_instruction, TRANS_DATA[key], whole_replacement)
			pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(whole_replacement))

def setOptionDialogue(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.option_dialogues


	dialogue_array = dialogue_json["data"]

	# 2 cases
	offsets = [e["offset"] for e in dialogue_array]

	og_instruction = utils.createOptionsDialogue([o + OG_DISTANCE for o in offsets])
	pos_instruction = OG_DATA.find(og_instruction)
	og_pos = pos_instruction

	for key in LANGUAGES:
		pos_instruction = og_pos
		form_texts = [FU.formatText(e[key]) for e in dialogue_array]

		is_overwritable = True
		for form, dia in zip(form_texts, dialogue_array):
			if len(form) > dia["size"]:
				is_overwritable = False
			if dia[key].count('\n') > info["n_lines"]:
				lines = info["n_lines"]
				raise ValueError(f"This text cannot have more than {lines} lines") # Just break
		

		if is_overwritable:
			for t, o in zip(form_texts, offsets):
				writeText(key, t, o)
			return

		# Make a new instruction
		new_adresses = []
		for t in form_texts:
			new_addr = writeText(key, t)
			new_addresses.append(new_addr)

		if pos_instruction == -1: 
			for o, n in zip(offsets, new_addresses):
				saveToErrorsPtr(o, n)
			return
		# Only bigger, change the ptr
		new_inst = utils.createOptionsDialogue([a + DISTANCE_TO_VIRTUAL for a in new_address])
		
		while pos_instruction != -1: #There might be more that one call to the value
			writeToHex(pos_instruction, TRANS_DATA[key], new_inst)
			pos_instruction = OG_DATA.find(og_instruction, pos_instruction + len(new_inst))
		
		# Cannot add more lines to this case

# ------- The next ones apper only once... I believe --------------------

def setItemDescription(dialogue_json):

	global TRANS_DATA
	info = dialogues_data.item_descriptions

	# Find the position in the table
	table_idx = utils.toBytesMIPS(dialogue_json["offset"] + OG_DISTANCE)
	pos_idx = OG_DATA.find(table_idx, info["table_idx"]-1)
	if pos_idx  - table_idx > 0x3C: # Length of table
		pos_idx = -1
 
	og_pos = pos_idx
	# Patch it accordingly
	for key in LANGUAGES:
		pos_idx = og_pos
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)

		if n_lines > info["n_lines"]:
			lines = info["n_lines"]
			raise ValueError(f"This text cannot have more than {lines} lines") # Just break

		if len(formated_text) <= dialogue_json["size"]:
			writeText(key, formated_text, dialogue_json["offset"])
			return

		# Write new

		if pos_idx == -1:
			raise ValueError("Tried to increase the size but the ptr to the original data was not found!")

		new_addr = writeText(key, formated_text)
		new_idx = utils.toBytesMIPS(new_addr + DISTANCE_TO_VIRTUAL)
		writeToHex(pos_idx, TRANS_DATA[key], new_idx)


def setLetterText(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.letters_text

	# Find the position in the table
	table_idx = utils.toBytesMIPS(dialogue_json["offset"] + OG_DISTANCE)
	pos_idx = OG_DATA.find(table_idx, info["table_idx"])
	if pos_idx  - table_idx > 0x28: # Length of table
		pos_idx = -1
 
	og_pos = pos_idx
	# PAtch it accordingly
	for key in LANGUAGES:
		pos_idx = og_pos
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)

		if n_lines > info["n_lines"]:
			lines = info["n_lines"]
			raise ValueError(f"This text cannot have more than {lines} lines") # Just break

		if len(formated_text) <= dialogue_json["size"]:
			writeText(key, formated_text, dialogue_json["offset"])
			return

		# Write new

		if pos_idx == -1:
			raise ValueError("Tried to increase the size but the ptr to the original data was not found!")

		new_addr = writeText(key, formated_text)
		new_idx = utils.toBytesMIPS(new_addr + DISTANCE_TO_VIRTUAL)
		writeToHex(pos_idx, TRANS_DATA[key], new_idx)


# Doesn't seem to be any easy instructions for these ones
# Temporary. Change later
def setTelephoneCall(dialogue_json):
	global TRANS_DATA
	info = dialogues_data.phone_calls
 
	
	# Patch it accordingly
	for key in LANGUAGES:
		text = dialogue_json[key]
		n_lines = text.count('\n') + 1

		formated_text = FU.formatText(text)

		if n_lines > info["n_lines"]:
			lines = info["n_lines"]
			raise ValueError(f"Cannot have more than {lines} lines")

		if len(formated_text) <= dialogue_json["size"]:
			writeText(key, formated_text, dialogue_json["offset"])
			return

		raise ValueError("Cannot change the position of a phone call dialogue for now")

"""
{
	"languages": ["en", "es"],
	"data": {o1:{},o2:{},o3:{},...}
}
"""
# The offset is for easy identification if it needs to be edited
def createVersions(json_data, exec_path):
	global LANGUAGES
	LANGUAGES = json_data["languages"]

	with open(exec_path, "r+b") as inputFile:
		global OG_DATA
		OG_DATA = bytearray(inputFile.read())

	global TRANS_DATA
	global OFFSET_TEXT
	global OFFSET_INSTRUCTIONS
	for key in LANGUAGES:
		TRANS_DATA[key] = copy.deepcopy(OG_DATA)
		#TRANS_DATA[key][0x2bc7d0:] = [0xFF] * (len(TRANS_DATA[key]) - 0x2bc7d0)

		# We map a section of the code to the PS2 memmory with this
		virtual_mem_addr = DISTANCE_TO_VIRTUAL + OG_OFFSET_INSTRUCTIONS - 0x1d0
		TRANS_DATA[key][0x5c:0x5c + 0x4] = utils.toBytesMIPS(virtual_mem_addr)
		TRANS_DATA[key][0x60:0x60 + 0x4] = utils.toBytesMIPS(virtual_mem_addr)

		# Set offsets
		OFFSET_TEXT[key] = OG_OFFSET_TEXT
		OFFSET_INSTRUCTIONS[key] = OG_OFFSET_INSTRUCTIONS

	for dialogue in json_data["data"].values():
		type = dialogue["type"]
		if type == 0:
			if dialogue['isMC']:
				setMCDialogue(dialogue)
			else:
				setGirlDialogue(dialogue)
		elif type == 1:
			setBlackDialogue(dialogue)
		elif type == 2:
			setOptionDialogue(dialogue)
		elif type == 3:
			setItemDescription(dialogue)
		elif type == 4:
			setLetterText(dialogue)
		elif type == 5:
			setTelephoneCall(dialogue)
			pass
		else:
			raise ValueError("Not a valid dialogue")

	for key in LANGUAGES:
		os.makedirs(key, exist_ok=True)
		new_exec = os.path.join(key, os.path.basename(exec_path))
		with open(new_exec, "wb") as file:
			file.write(TRANS_DATA[key])

	print(ERRORS_JAL)
	print(ERRORS_PTR)

if __name__ == '__main__':

	slps_path = sys.argv[1] #Path to SLPS_255.47 to modify
	json_path = sys.argv[2]

	with open(json_path, "r", encoding="utf8") as f:
		data = json.load(f)
		createVersions(data, slps_path)