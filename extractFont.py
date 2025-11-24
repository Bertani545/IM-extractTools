from PIL import Image
import os

# Base parameters
WIDTH = 22
HEIGHT = 22
GLYPH_SIZE = WIDTH * HEIGHT
START_OFFSET = 0x7fd4 -22 #0x399000 + 0x2fd4 - 22# Hard coded start of the text in file. Either works, unfortunately
# Input file
INPUT_FILE = "DATA0.DAT"

# Output folder
OUTPUT_DIR = "glyphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Read the file
with open(INPUT_FILE, "rb") as file:
    file.seek(START_OFFSET)
    index = 1

    while index <= 4887: # Hard coded
        glyph_data = file.read(GLYPH_SIZE)
        if len(glyph_data) < GLYPH_SIZE:
            break  # Stop at EOF or incomplete data

        # Create the grayscale image
        image = Image.new("L", (WIDTH, HEIGHT))
        image.putdata(list(glyph_data))

        # Save with padded index (01, 02, 03...)
        filename = os.path.join(OUTPUT_DIR, f"{index:02d}.png")
        image.save(filename)
        print(f"Saved {filename}")

        index += 1

print("Done!")

