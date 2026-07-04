import hashlib
import hmac
import os

secret = os.environ.get('SECRET_KEY').encode('utf-8')

def func(stream_view):
    stream_len = len(stream_view)

    if stream_len < 35:
        return None
    
    l = 0
    while l < stream_len - 32:
        if stream_view[l] == 0xAA and stream_view[l + 1] == 0xBB:
            
            payload_len = stream_view[l + 2]

            r = l + 3 + payload_len
            if r + 32 > stream_len:
                return None
            
            signature = hmac.new(secret, stream_view[l + 3: r], hashlib.sha256)

            if not hmac.compare_digest(signature.digest(), stream_view[r: r + 32]):
                return None
            
            return stream_view[l + 3: r]
        
        l += 1

    return None


if __name__ == "__main__":
    raw_bytes = b"\x12\x12\xAA\x12\x12\xeE\xAA\xBB\x05\xDE\xDE\xAD\xBE\xEF\xf1\x17\xa3\xc6\x4c\x78\x10\xfd\x60\xed\x52\xd9\x9d\x49\xe4\xec\x95\xab\x67\x61\x4a\xcc\x3d\x9d\x71\xea\xa0\x91\x8c\xb7\xfe\xc4"
    view = memoryview(raw_bytes)
    result = func(view)
    if result:
        print("Valid bytes!")
        print(result.tobytes())
    else:
        print("Invalid bytes!, check hmac or payload length")