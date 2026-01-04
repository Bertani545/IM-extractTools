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
	'C': b'\xA6\x04\x09',
	'I': b'\xA6\x04\x0f',
	'W': b'\xA6\x04\x1d',

	'ñ': b'#', # Modified in the font # -> ñ

	# Safety
	'á': b'a', 
	'é': b'e',
	'í': b'i',
	'ó': b'o',
	'ú': b'u',
	'Á': b'A',
	'É': b'E',
	'Í': b'I',
	'Ó': b'O',
	'Ú': b'U',
	'¿': b'',
	'¡': b''
}

LINE_SIZE = 28

def prepareTextForSearch(text):
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
			flag = text[i:i+4]
			try:
				hex_val = int(flag, 16)
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

	return bytes(out)

def getCharSize(ch):
    """Return byte length based on custom letters map or encoding."""
    if ch in output_letters:
        return len(output_letters[ch])
    else:
        return len(ch.encode(encoding, errors="replace"))



def getTextSize(text):
	formated = formatText(text)
	return(len(formated))

def checkLines(text):
	lines = text.split('\n')
	for i, line in enumerate(lines):
		clean = re.sub(r"0x.", "", line)
		if len(clean) > LINE_SIZE:
			return i
	return -1