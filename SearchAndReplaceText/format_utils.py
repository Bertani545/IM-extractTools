# This is specific for the PS2 game Ichigo Mashimaro
# Change this map to your language necessities
letters = {
	# Neccesary ones
	'C': b'\x4b\x04\x09',
	'I': b'\x4b\x04\x0f',
	'W': b'\x4b\x04\x1d',

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
				hex_val = int(text[i+2:i+4], 16)
			except:
				hex_val = b'\x00'
			out.append(hex_val)
			i += 4
			continue
		if ch in letters:
			out += letters[ch]
		else:
			out += ch.encode("shift_jis", errors="replace")
			
		i += 1

	return bytes(out)

def getCharSize(ch):
    """Return byte length based on custom letters map or shift_jis encoding."""
    if ch in letters:
        return len(letters[ch])
    else:
        return len(ch.encode("shift_jis", errors="replace"))



def getTextSize(text):
	formated = formatText(text)
	return(len(formated))