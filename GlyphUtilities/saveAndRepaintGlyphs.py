from PIL import Image
import os
import numpy as np
import cv2

# Takes a certain glyph by id (obtained from extractFont.py) and allows you to edit it.
# After that, it's saved to a file with the new idx

BRUSH_SIZE = 1   # in glyph pixels
DRAW_VALUE = 255
ERASE_VALUE = 0
ZOOM = 20

drawing = False
erasing = False




WIDTH = 22
HEIGHT = 22
GLYPH_SIZE = WIDTH * HEIGHT
START_OFFSET_1 = 0x7fd4 - 22
START_OFFSET_2 = 0x399000 + 0x2fd4 - 22
#GLYPH_NUMBER = 83

OUTPUT_DIR = "my_glyphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pairs    
# First: The index of the glyph you want to use as base
# Second: The index of the glyph you want to replace.
GLYPH_MAP = [
	# Character names
	(1934, 1934),
	(1204, 1204),
	(2088, 2088),
	(733, 733),
	(419, 419),
	(420, 420),
	(2861, 2861),
	(614, 614),
	(291, 291),
	(331, 331),
	(1542, 1542),
	(2436, 2436),

	# Spanish stuff
	(194, 207), # ñ
	(169, 208),# Ñ
	(182, 209),# á
	(186, 210),# é
	(190, 211),# í
	(195, 212),# ó
	(201, 213),# ú
	(201, 214),# ü
	(156, 215),# Á
	(160, 216),# É
	(164, 217),# Í
	(170, 218),# Ó
	(176, 219),# Ú
	(176, 220),# Ü
	(7, 221),# ¿
	(8, 222),# ¡
]

INPUT_FILE = "DATA0.DAT"

def paint(x, y, erase=False):
	gx = x // ZOOM
	gy = y // ZOOM

	if gx < 0 or gx >= WIDTH or gy < 0 or gy >= HEIGHT:
		return

	kernel = [
		[10, 64, 10],
		[64, 255, 64],
		[10, 64, 10]
	]



	for ky in range(-1, 2):
		for kx in range(-1, 2):
			px = gx + kx
			py = gy + ky

			if 0 <= px < WIDTH and 0 <= py < HEIGHT:
				strength = kernel[ky + 1][kx + 1]

				# if painting, take max (so painting overwrites)
				if not erase:
					img[py, px] = max(img[py, px], strength)
				else:
					img[py, px] = 0

	# Update display image
	disp[:] = cv2.resize(img, (WIDTH * ZOOM, HEIGHT * ZOOM),
						 interpolation=cv2.INTER_NEAREST)

ERASE = False
def mouse_event(event, x, y, flags, param):
	global drawing, erasing

	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
		paint(x, y, ERASE)

	elif event == cv2.EVENT_RBUTTONDOWN:
		'''
		erasing = True
		paint(x, y, erase=True)
		'''

	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing:
			paint(x, y, ERASE)


	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
	'''
	elif event == cv2.EVENT_RBUTTONUP:
		erasing = False
	'''

print("Controls:")
print("  Left mouse: draw (white)")
print("  Right mouse: erase (black)")
print("  S: save and write back to DAT")
print("  Q: quit without saving")

with open(INPUT_FILE, "r+b") as file:

	for og_id, new_id in GLYPH_MAP:

		file.seek(START_OFFSET_1 + og_id * GLYPH_SIZE)
		glyph_data = file.read(GLYPH_SIZE)

		# Edit image
		img = np.frombuffer(glyph_data, dtype=np.uint8).reshape((HEIGHT, WIDTH)).copy()
		disp = cv2.resize(img, (WIDTH * ZOOM, HEIGHT * ZOOM), interpolation=cv2.INTER_NEAREST)


		cv2.namedWindow("Glyph Editor", cv2.WINDOW_NORMAL)
		cv2.setMouseCallback("Glyph Editor", mouse_event)




		while True:
			cv2.imshow("Glyph Editor", disp)
			key = cv2.waitKey(10)

			if key in (ord('q'), ord('Q')):
				break

			if key in (ord('e'), ord('E')):
				ERASE = not ERASE

			if key in (ord('s'), ord('S')):
				# Save glyph back
				
				image = Image.new("L", (WIDTH, HEIGHT))
				image.putdata(img.reshape(HEIGHT * WIDTH))

				# Save as image and have a new py file to save them to the 
				filename = os.path.join(OUTPUT_DIR, f"{new_id:02d}.png")
				image.save(filename)
				print(f"Saved {filename}")

				print("Glyph saved.")
				break

		cv2.destroyAllWindows()


