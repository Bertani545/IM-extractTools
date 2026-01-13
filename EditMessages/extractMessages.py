import struct
from PIL import Image
import numpy as np
import os
import json
import shutil


target_hex = "400000000fc5bd43"
target_bytes = bytes.fromhex(target_hex)
PIXEL_SIZE = 4  # RGBA
READ_PIXELS = 21 * 8        # 256
SKIP_PIXELS = (32 * 8) * (4 * 8)  # 8192
TOTAL_READ_PER_BLOCK = 640  # pixels per sequence
#REPEATS = 448 // (8 * 4)             # 32 sequences
NEXT_START_OFFSET_PIXELS = (64 * 8) * (4*8) + 16 * 8 # 16448
NEXT_START_OFFSET_BYTES = NEXT_START_OFFSET_PIXELS * PIXEL_SIZE
OUTPUT_DIR = "messages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#base_offset = start of the picture data
def extract_blocks(data, base_offset, h , w):
    image = np.zeros((h, w + 3 * 8, 4), dtype=np.uint8)
    print("Size: ", w,h)
    REPEATS = (h+31)//32
    length = w + 3 * 8;
    current_length = 0;
    total_length = 0;
    line_curr_size = 0;
    line_size = 32 * 8; # HARD CODED <----- This is the size of the blocks
    START = base_offset
    TOTAL_LINES = 0
    while(TOTAL_LINES < h):
        #print()
        #print(current_length)
        line_curr_size = 0
        base_offset = START
        while (line_curr_size < line_size and TOTAL_LINES < h):
            offset = base_offset
            last_len = current_length
            current_length = min(length - current_length, line_size - line_curr_size)
            total_length += current_length
            #print(current_length, total_length)

            TIMES = min(32, h - TOTAL_LINES)
            for j in range(TIMES):
                start = offset
                end = start + (current_length) * PIXEL_SIZE# READ_PIXELS * PIXEL_SIZE
                row_pixels = np.frombuffer(data[start : end], dtype=np.uint8).reshape(-1,4)

                for col in range(current_length):
                    pixel = row_pixels[col][::-1].copy()
                    pixel[3] = 255                                              ## This is extra
                    image[TOTAL_LINES + j, col + last_len] = pixel

                offset += (32)*8 * PIXEL_SIZE #32 * 8 * PIXEL_SIZE
            base_offset += current_length * 4
            line_curr_size += current_length
            if (total_length == length):
                TOTAL_LINES += 32
                #base_offset += 3 * 8 * 4
                total_length = 0
                #line_curr_size += 3 * 8
                current_length = 0

        START += (32 * 8 * TIMES) * PIXEL_SIZE#(4 * (16*8) * (4 * 8) + 16 * 8) * PIXEL_SIZE

    return image



with open("DATA0.DAT", "rb") as f:
    data = f.read()

base = 0x152802e0
i = 0
with open(os.path.join(OUTPUT_DIR, "offsets.json"), 'w', encoding="utf8") as output:
    output.seek(0)
    json_data = {}
    while (True):
        idx = data.find(target_bytes, base)
        if (idx == -1 or idx > 0x165ca2e0):
            break
        special_num = data[idx + 0xD]
        print(i , special_num)
        header_offset = 0
        if (special_num == 1):
            header_offset = 0x0ff
        elif (special_num == 2):
            header_offset = 0x1ff
        base = idx + header_offset
        #0x30 skips the first part of the header, reaaches the other magic number
        size_data = data[idx + 0x40 + len(target_bytes) : idx + 0x40 + len(target_bytes) + 4]    
        if (len(size_data) < 4):
            break
        width = struct.unpack("<H", size_data[0:2])[0]
        height = struct.unpack("<H", size_data[2:4])[0]
        if (not ((width > 0 and width <= 640) and (height > 0 and height <= 448))):
            continue

        base_offset = idx + header_offset
        raw_data = extract_blocks(data, base_offset, height, width)

        img = Image.fromarray(raw_data, "RGBA")
        filename = os.path.join(OUTPUT_DIR, f"{i:02d}.png")
        img.save(filename)


        json_data[str(i)] = base_offset

        i+=1

    json.dump(json_data, output, ensure_ascii=False, indent=4)

    
