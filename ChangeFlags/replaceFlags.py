BASE_OFFSET = 0x4C43C
STRIDE = 0x0C

letters = [
    'K', 'C', 'I', 'S', 'F', 'D', 'J',
    'T', 'P', 'W', 'O', 'B', 'G', 'R', 'Q'
]

# The unchanged ones break the parser when changed
map_letters = {
    'B': b'\xA1',
    'C': b'C',
    'D': b'\xA2',
    'F': b'\xA3',
    'G': b'\xA4',
    'I': b'I',
    'J': b'\xA5',
    'K': b'\xA6',
    'O': b'\xA7',
    'P': b'\xA8',
    'Q': b'\xA9',
    'R': b'\xAA',
    'S': b'\xAB',
    'T': b'\xAC',
    'W': b'W'
}


def patch_file(path):
    with open(path, 'r+b') as f:
        for i, letter in enumerate(letters):
            offset = BASE_OFFSET + i * STRIDE
            new_byte = map_letters[letter]

            f.seek(offset)
            f.write(bytes(new_byte))

            print(f"{letter} @ {hex(offset)} -> {new_byte}")

if __name__ == "__main__":
    patch_file("SLPS_255.47")
