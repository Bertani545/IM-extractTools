import os

FILE = "SLPS_255.47"
APPEND_SIZE = 0x200000
VIRTUAL_ADDRES = 0x1500000

# Change the flags by default for execution
def make_bigger(data, extra_size, new_virt_adress):
	# Format data
	size_hex = extra_size.to_bytes(4, byteorder='little')
	addr_hex = new_virt_adress.to_bytes(4, byteorder='little')

	# Patch
	data[0x6C] = 0x7 # New flag
	data[0x5c:0x5c+4] = addr_hex
	data[0x60:0x60+4] = addr_hex
	data[0x64:0x64+4] = size_hex
	data[0x68:0x68+4] = size_hex

	data += b'\x00' * extra_size

	new_dir = 'new'
	os.makedirs(new_dir, exist_ok=True)

	new_path = os.path.join('new', FILE)
	with open(new_path, 'wb') as f:
		f.write(data)

if __name__ == '__main__':
	with open(FILE, 'rb') as f:
		data = bytearray(f.read())
		make_bigger(data, APPEND_SIZE, VIRTUAL_ADDRES)

