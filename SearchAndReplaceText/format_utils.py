import re
# This is specific for the PS2 game Ichigo Mashimaro
# Change the initial data for your game

encoding = "shift_jis"


# Map of characters that the game uses
letters_map = {
	'a': b'a',
	"あ": b'\x82\xa0',
	"お": b'\x82\xa8',
}

# Map of characters for the new version that you are creating
output_letters = {
	# Neccesary ones
	'B': b'\x4B\x04\x08',
	'C': b'\x4B\x04\x09',
	'D': b'\x4B\x04\x0a',
	'F': b'\x4B\x04\x0c',
	'G': b'\x4B\x04\x0d',
	'I': b'\x4B\x04\x0f',
	'J': b'\x4B\x04\x10',
	'K': b'\x4B\x04\x11',
	'O': b'\x4B\x04\x15',
	'P': b'\x4B\x04\x16',
	'Q': b'\x4B\x04\x17',
	'R': b'\x4B\x04\x18',
	'T': b'\x4B\x04\x1a',
	'W': b'\x4B\x04\x1d',

	# Added by modifying the font
	'ñ': b'\x9f\xa6',
	'Ñ': b'\x9f\xa7',
	'á': b'\x9f\xa8',
	'é': b'\x9f\xa9',
	'í': b'\x9f\xaa',
	'ó': b'\x9f\xab',
	'ú': b'\x9f\xac',
	'ü': b'\x9f\xad',
	'Á': b'\x9f\xae',
	'É': b'\x9f\xaf',
	'Í': b'\x9f\xb0',
	'Ó': b'\x9f\xb1',
	'Ú': b'\x9f\xb2',
	'Ü': b'\x9f\xb3',
	'¿': b'\x9f\xb4',
	'¡': b'\x9f\xb5',
}

def prepareTextForSearch(text, start, end):
	text = start + text + end
	encoded = bytearray(text.encode(encoding))
	for chara, replacement in letters_map.items():
		target = chara.encode(encoding)

		start = 0
		while True:
			pos = encoded.find(target, start)
			if pos == -1:
				break
			encoded[pos:pos + len(target)] = replacement
			start = pos + len(replacement)
	return bytes(encoded)

# To UTF-8
def decodeGameText(byte_array):
	data = bytearray(byte_array)
	for chara, game_bytes in letters_map.items():
		utf8_bytes = chara.encode(encoding)

		start = 0
		while True:
			pos = data.find(game_bytes, start)
			if pos == -1:
				break

			data[pos:pos + len(game_bytes)] = utf8_bytes
			start = pos + len(utf8_bytes)
	return data.decode(encoding, errors="strict")





#Example
# 0xA1This is light blue
def formatText(text):
	out = bytearray()
	i = 0
	length = len(text)
	while i < length:
		ch = text[i]
		if i+4 <= length and text[i:i+2] == "0x": #hex flag
			flag = text[i:i+3]
			try:
				hex_val = ord(text[2]) # Changed this now that flags are letters
			except:
				hex_val = 0
			out.append(hex_val)
			i += 4
			continue
		if ch in output_letters:
			out += output_letters[ch]
		else:
			out += ch.encode(encoding, errors="replace")
			
		i += 1

	return bytes(out) + b'\x00'

def getCharSize(ch):
    """Return byte length based on custom letters map or encoding."""
    if ch in output_letters:
        return len(output_letters[ch])
    else:
        return len(ch.encode(encoding, errors="replace"))



def getTextSize(text):
	formated = formatText(text)
	return(len(formated))

def checkLines(text, line_size):
	lines = text.split('\n')
	for i, line in enumerate(lines):
		clean = re.sub(r"0x.", "", line)
		if len(clean) > line_size:
			return i
	return -1

def complyLineSize(text, line_size=28):
	mod_line = checkLines(text, line_size)
	while(mod_line != -1):
		lines = text.split('\n')
		to_mod = lines[mod_line]
		lines[mod_line] = to_mod[:line_size] + '\n' + to_mod[line_size:]
		text = "\n".join(lines)
		mod_line = checkLines(text, line_size)
	return text

