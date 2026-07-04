# Imagine you are writing a custom packet parser for a network stream or a binary log file.
#  The protocol specifies that every valid frame must start with a specific magic byte sequence 
# (e.g., [0xAA, 0xBB]), followed by a length byte, and then the payload data.

# If an attacker modifies the stream to have a corrupted length byte, or 
# injects junk data between valid frames, a naive parser might read out of bounds or crash.

# Design a zero-copy boundary parser that checks if our data stream follows the expected format.


def parse(stream_view):
    stream_len = len(stream_view)

    if stream_len < 3:
        return None
    
    l = 0 
    while l <= stream_len - 3:
        if stream_view[l] == 0xAA and stream_view[l + 1] == 0xBB:
            payload_len = stream_view[l + 2]
            
            r = l + 3 + payload_len
            # boundary check (security)
            if r <= stream_len:

                return stream_view[l + 3:r]
        l += 1
    
    return None

if __name__ == "__main__":
    raw_bytes = b"\x12\xAA\xBB\x04\xDE\xAD\xBE\xEF\x99"
    view = memoryview(raw_bytes)

    result = parse(view)
    print(result.tobytes())