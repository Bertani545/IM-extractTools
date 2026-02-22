def toBytesMIPS(integer:int):
	return integer.to_bytes(4, "little")


def createJalInstruction(target_addr: int) -> str:
	if target_addr % 4 != 0:
		raise ValueError("Target address must be 4-byte aligned.")
	index = (target_addr >> 2) & 0x03FFFFFF
	instruction = (0x03 << 26) | index
	return toBytesMIPS(instruction)


def createLi(val:int, a:int):
	register = a + 4
	return toBytesMIPS((0x09 << 26) | (0 << 21) | (register << 16) | (val & 0xFFFF))

def createAddiu(val:int, a:int):
	register = a + 4
	return toBytesMIPS((0x09 << 26) | (register << 21) | (register << 16) | (val & 0xFFFF))

def createLui(val:int, a:int):
	register = a + 4
	return toBytesMIPS((0x0F << 26) | (register << 16) | (val & 0xFFFF))

def createAdrressParam(new_addres:int, a: int):
	upper = (new_addres + 0x8000) >> 16
	lower = new_addres & 0xFFFF

	lui = createLui(upper, a)
	addiu = createAddiu(lower, a)

	return lui, addiu

move0ToA1 = b'\x2d\x28\x00\x00'
move0ToA2 = b'\x2d\x30\x00\x00'

def createMCDialogue(dialogue_pos):
	jal = b'\xb4\xce\x04\x0c'
	lui, addiu = createAdrressParam(dialogue_pos, a=0)
	return	lui + jal + addiu

def createGirlsDialogue(dialogue_pos, audio_id=0):
	jal = b'\x44\xce\x04\x0c'
	lui, addiu = createAdrressParam(dialogue_pos, a=0)

	if audio_id == 0:
		audio_in = move0ToA1
	else:
		audio_in = createLi(audio_id, a=1)
	return lui + audio_in + addiu + jal + move0ToA2

def createOptionsDialogue(dialogue_pos_array):
	n_dialogues = len(dialogue_array)
	if n < 2:
		raise ValueError("Not a valid dialogue option")

	jal = b'\x6c\xcd\x04\x0c'
	extra = b'\xff\xff\x07\x24'
	lui1, addiu1 = createAdrressParam(dialogue_pos_array[0], a=0)
	lui2, addiu2 = createAdrressParam(dialogue_pos_array[1], a=1)

	instruction = b''
	if n_dialogues == 2:
		instruction = lui1 + lui2 + \
					  addiu1 + addiu2 + \
					  move0ToA2 + \
					  jal + extra

	elif n_dialogues == 3:
		lui3, addiu3 = createAdrressParam(dialogue_pos_array[2], a=2)
		
		instruction = lui1 + lui2 + lui3 + \
					  addiu1 + addiu2 + addiu3 + \
					  jal + extra

	return instruction

def createBlackDialogue(dialogue_pos):
	jal = b'\xc0\xcd\x04\x0c'
	lui, addiu = createAdrressParam(dialogue_pos, a=0)
	return lui + move0ToA1 + jal + addiu

def createPauseInstruction():
	return b'\x70\xd0\x04\x0c\x00\x00\x00\x00' # jal + nop



functionDefinition = b'\xf0\xff\xbd\x27\x00\x00\xbf\xff'
functionReturn = b'\x00\x00\xbf\xdf\x2d\x10\x00\x00\x08\x00\xe0\x03\x10\x00\xbd\x27\x00\x00\x00\x00'

stop_function = b'\x70\xd0\x04\x0c\x00\x00\x00\x00'


def extractValFromLi(li_hex):
	imm = li_hex & 0xFFFF

	if imm & 0x8000:
		imm -= 0x10000

	return imm