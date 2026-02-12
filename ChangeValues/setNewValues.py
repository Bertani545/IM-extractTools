import sys
import os
import shutil

def set_value(file, offset, value):
	file.seek(offset)
	file.write(bytes([value]))

def set_game_new_values(file_path):
	os.makedirs("new", exist_ok=True)
	new_exec = os.path.join("new", os.path.basename(file_path))
	shutil.copyfile(file_path, new_exec)

	with open(new_exec, "r+b") as f:
		set_value(f, 0x2268f8, 0x1C) # Total of characters per line
		set_value(f, 0x226908, 0x23) # Total of characters per line, intro (doesn't work)
		set_value(f, 0x22690c, 0x03) # Total lines in intro (doesn't work)
		set_value(f, 0x226940, 0x0F) # Text Spacing in game
		set_value(f, 0x226948, 0x0F) # Text Spacing in introduction
		set_value(f, 0x226d88, 0x0F) # Set spacing for options
		# Set new flags
		'''
		set_value(f, 0x4C43C, 0xA6) # K
		set_value(f, 0x4C460, 0xAB) # S
		set_value(f, 0x4C46C, 0xA3) # F
		set_value(f, 0x4C478, 0xA2) # D
		set_value(f, 0x4C484, 0xA5) # J
		set_value(f, 0x4C490, 0xAC) # T
		set_value(f, 0x4C49C, 0xA8) # P
		set_value(f, 0x4C4B4, 0xA7) # O
		set_value(f, 0x4C4C0, 0xA1) # B
		set_value(f, 0x4C4CC, 0xA4) # G
		set_value(f, 0x4C4D8, 0xAA) # R
		set_value(f, 0x4C4E4, 0xA9) # Q
		'''

		f.flush()


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python setNewvalues.py file")
		sys.exit(1)
	
	file_path = sys.argv[1] #Path to SLPS_255.47 to modify
	set_game_new_values(file_path)