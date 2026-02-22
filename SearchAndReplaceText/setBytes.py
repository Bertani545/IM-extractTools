# IT WORKSSSSS!!!!

INPUT_FILE  = "SLPS_255.bak"
OUTPUT_FILE = "SLPS_255.47"

HEX_OFFSET  = "0x1A2B"        # Hex offset as string (e.g. "0x1A2B" or "1A2B")
HEX_BYTES   = "f0 ff bd 00"   # Bytes to write (spaces optional)

# =======================
# IMPLEMENTATION
# =======================

def parse_hex_bytes(s):
    s = s.replace(" ", "")
    if len(s) % 2 != 0:
        raise ValueError("Hex byte string must have even length")
    return bytes.fromhex(s)

def patch(data, offset, hex_bytes):
    patch_bytes = parse_hex_bytes(hex_bytes)
    if offset < 0:
        raise ValueError("Offset must be non-negative")
    end = offset + len(patch_bytes)
    if end > len(data):
        raise ValueError("Not enough bytes")

    data[offset:end] = patch_bytes

def main():
    
    with open(INPUT_FILE, "rb") as f:
        data = bytearray(f.read())

    # where? ghidra says - 0xC
    # how many? jump + 0x14 zero bytes
    info = "74 00 54 0c 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    patch(data, 0x85ee0, info)

    # Where we store the instruction
    info = "f0 ff bd 27 00 00 bf ff 34 00 04 3c 2d 28 00 00 c0 cd 04 0c 5f 4d 84 24 70 d0 04 0c 00 00 00 00 34 00 04 3c 2d 28 00 00 c0 cd 04 0c 5f 4d 84 24 70 d0 04 0c 00 00 00 00 00 00 bf df 2d 10 00 00 08 00 e0 03 10 00 bd 27 00 00 00 00"
    patch(data, 0x2bc7d0, info)


    with open(OUTPUT_FILE, "wb") as f:
        f.write(data)

    '''
    print(
        f"Wrote {len(patch_bytes)} bytes at offset 0x{offset:X} "
        f"from '{INPUT_FILE}' -> '{OUTPUT_FILE}'"
    )
    '''

if __name__ == "__main__":
    main()
