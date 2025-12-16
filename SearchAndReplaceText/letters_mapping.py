# The Mayus chars in this map are used for flags in the engine, so a work around is needed
# Characters not in the font should map to a ascii one for ease of use
# Change this map to your language necessities
letters = {
	# Neccesary ones
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
	'Í': b'\x4b\x04\x0f',
	'Ó': b'\x4b\x04\x15',
	'Ú': b'U',
	'¿': b'',
	'¡': b''
}