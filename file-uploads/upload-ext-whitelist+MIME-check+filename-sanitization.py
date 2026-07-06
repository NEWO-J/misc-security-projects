import shutil
from pathlib import Path
import random
import string

allowed_ext = set([".png",".jpg",".jpeg",".gif"])
allowed_magicb = set([b'\x89PNG\r\n\x1a\n', b'\xff\xd8',b'GIF8'])
dst_path = "./auxiliary/file-uploads/"
characters = string.ascii_letters + string.digits

def upload_check(filename):
    ext = Path(filename).suffix

    if ext.lower() not in allowed_ext:
        return False
    
    # MIME check logic
    try:
        with open(filename, "rb") as f:
            bytecount = 2
            valid = False
            magic_bytes = f.read(bytecount)
            while not valid and bytecount <= 8:
                if magic_bytes in allowed_magicb:
                    valid = True
                    break
                bytecount += 1
                f.seek(0)
                magic_bytes = f.read(bytecount)
            
            # sanitize original filename
            if valid:
                new_filename = ''.join(random.choices(characters, k=15)) + ext
                shutil.copy(filename, dst_path + new_filename)
                return True
            
            return False
    except FileNotFoundError as e:
        print("No such file found!", e)
        return False
    


if __name__ == "__main__":
    filename = "ignored_data/land.jpg"
    result = upload_check(filename)
    if result:
        print("Upload successful")
    else:
        print("Upload failed")