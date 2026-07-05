import shutil

allowed_ext = set(["png","jpg","jpeg","gif"])
dst_path = "./auxiliary/file-uploads/"

def upload_check(filename):
    try:
        file,ext = filename.split(".")
    except ValueError:
        raise ValueError("Ensure filenames only contain one extension")
    
    if ext.lower() not in allowed_ext:
        return False
    
    output = (dst_path + filename)

    try:
        shutil.copy(filename, output)
        return True
    except FileNotFoundError as e:
        print("No such file found!", e)
        return False

if __name__ == "__main__":
    filename = "dog.PNg"
    result = upload_check(filename)
    if result:
        print("Upload successful")
    else:
        print("Upload failed")