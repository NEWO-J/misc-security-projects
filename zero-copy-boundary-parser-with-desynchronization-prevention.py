

def parse_w_desync_check(stream_view):
    if len(stream_view) < 3:
        return None
    
    l = 0
    while l < len(stream_view) - 3:
        if stream_view[l] == 0xAA and stream_view[l + 1] == 0xBB:
            print("d")
            payload_len = stream_view[l + 2]
            r = l + 3 + payload_len


            if len(stream_view) < r + 1:
                # security exit
                return None
            
            if stream_view[r] != 0x00:
                # security exit
                return None
        
            
            return stream_view[l + 3: r]
        
        l += 1

    print("e")
    return None

if __name__ == "__main__":
    raw_bytes = b"\x12\x12\xAA\x12\x12\x12\xAA\xBB\x0\xDE\xAD\xBE\xEF\x00\x12\x12\x12\x12"

    view = memoryview(raw_bytes)

    result = parse_w_desync_check(view)
    if result:
        print(result.tobytes())
    else:
        print("Not found")