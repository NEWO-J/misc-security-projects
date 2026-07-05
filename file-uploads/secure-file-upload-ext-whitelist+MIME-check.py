import shutil
from pathlib import Path

allowed_ext = set([".png",".jpg",".jpeg",".gif"])
allowed_magicb = set([b'\x89PNG\r\n\x1a\n', b'\xff\xd8'])
dst_path = "./auxiliary/file-uploads/"

def upload_check(filename):
    ext = Path(filename).suffix

    if ext.lower() not in allowed_ext:
        return False
    
    output = Path(dst_path + filename)
    
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
            
            if valid:
                shutil.copy(filename, output)
                return True
            print("not valid")
            return False
    except FileNotFoundError as e:
        print("No such file found!", e)
        return False
    


if __name__ == "__main__":
    filename = "land.jpg"
    result = upload_check(filename)
    if result:
        print("Upload successful")
    else:
        print("Upload failed")