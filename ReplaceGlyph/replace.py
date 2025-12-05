from PIL import Image
import os
import numpy as np
import cv2

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
GLYPH_NUMBER = 83
NEW_GLYPH_NUMBER = 195

INPUT_FILE = "DATA0.DAT"

with open(INPUT_FILE, "rb") as file:

	# Search n because we are going to draw an nn
	file.seek(START_OFFSET_1 + (NEW_GLYPH_NUMBER-1)*GLYPH_SIZE)
	glyph_data = file.read(GLYPH_SIZE)

	# Edit image
img = np.frombuffer(glyph_data, dtype=np.uint8).reshape((HEIGHT, WIDTH)).copy()
disp = cv2.resize(img, (WIDTH * ZOOM, HEIGHT * ZOOM), interpolation=cv2.INTER_NEAREST)

def paint(x, y, erase=False):
	gx = x // ZOOM
	gy = y // ZOOM

	if gx < 0 or gx >= WIDTH or gy < 0 or gy >= HEIGHT:
		return

	kernel = [
		[64, 128, 64],
		[128, 255, 128],
		[64, 128, 64]
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
					img[gx, gy] = 0

	# Update display image
	disp[:] = cv2.resize(img, (WIDTH * ZOOM, HEIGHT * ZOOM),
						 interpolation=cv2.INTER_NEAREST)


def mouse_event(event, x, y, flags, param):
	global drawing, erasing

	if event == cv2.EVENT_LBUTTONDOWN:
		drawing = True
		paint(x, y, erase=False)

	elif event == cv2.EVENT_RBUTTONDOWN:
		erasing = True
		paint(x, y, erase=True)

	elif event == cv2.EVENT_MOUSEMOVE:
		if drawing:
			paint(x, y, erase=False)
		elif erasing:
			paint(x, y, erase=True)

	elif event == cv2.EVENT_LBUTTONUP:
		drawing = False
	elif event == cv2.EVENT_RBUTTONUP:
		erasing = False

cv2.namedWindow("Glyph Editor", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Glyph Editor", mouse_event)

print("Controls:")
print("  Left mouse: draw (white)")
print("  Right mouse: erase (black)")
print("  S: save and write back to DAT")
print("  Q: quit without saving")


while True:
	cv2.imshow("Glyph Editor", disp)
	key = cv2.waitKey(10)

	if key in (ord('q'), ord('Q')):
		break

	if key in (ord('s'), ord('S')):
		# Save glyph back
		edited_bytes = img.astype(np.uint8).tobytes()
		with open(INPUT_FILE, "r+b") as file:
			file.seek(START_OFFSET_1 + (GLYPH_NUMBER - 1) * GLYPH_SIZE)
			file.write(edited_bytes)

			file.seek(START_OFFSET_2 + (GLYPH_NUMBER - 1) * GLYPH_SIZE)
			file.write(edited_bytes)

		print("Glyph saved.")
		break

cv2.destroyAllWindows()


