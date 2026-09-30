import argparse
from pathlib import Path
import requests
import tarfile
import json
import msgpack
import os

parser = argparse.ArgumentParser()

parser.add_argument('-u','--publish',help="Publish a package to the SPM registry - --publish <path/to/package.spm>", nargs='?', const=Path.cwd(), required=False)
parser.add_argument('-g','--get',help="Download a package", required=False)

args = parser.parse_args()

if not args.publish and not args.get:
    raise Exception("Error! please specify an argument (--publish or --get)")
if args.publish and args.get:
    raise Exception("Invalid argument")

def Publish(path):
    target_dir = Path(path) 
    name = target_dir.stem
    output_file = target_dir.parent / f"{name}.spm"
    with tarfile.open(output_file, "w:gz") as tar:
        print("archiving..")
        for item in  target_dir.iterdir():
            if item.name.lower() == "meta.json":
                with open(item, "r", encoding="utf-8") as json_file:
                    data = json.load(json_file)
                with open(target_dir / "meta.msgpack", "wb") as msgpack_file:
                    msgpack.pack(data, msgpack_file)
                os.remove(item)

                with open(target_dir / "meta.msgpack", "rb") as f:
                        file_bytes = f.read()
                        metadata = msgpack.unpackb(file_bytes, raw=False)
                        print(metadata["package_name"])
                continue
                 
            tar.add(item, arcname=item.name)

    with output_file.open("rb") as f:
            file = {"file": f}
            r = requests.post("http://localhost:8001/upload", files=file)
            print("sent")
            return r.text


if args.publish:
    print(Publish(args.publish))