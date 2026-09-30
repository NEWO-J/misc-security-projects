from fastapi import FastAPI, Body, HTTPException, UploadFile, File
from typing import Annotated
import tarfile
from pathlib import Path
import secrets
import shutil
from aws_blob_storage_connector.aws_connector import blob_upload
from ingestion_service import validate, security_check
import msgpack
import os

app = FastAPI()

@app.post("/upload")
def upload_pkg(
    file: Annotated[UploadFile, File()],
):
    
    if not file:
        raise HTTPException(status_code=401, detail="Package parameter missing")

    if file.size > 100000000:
        raise HTTPException(status_code=401, detail="Package size exceeds maximum 100 MB")

    max_ratio = 10
    extraction_path = secrets.token_hex(20)

    running_uncompressed_total = 0
    try:
        with tarfile.open(fileobj=file.file, mode="r") as tar:
            for member in tar:
                running_uncompressed_total += member.size
                current_ratio = running_uncompressed_total / file.size

                if current_ratio > max_ratio:
                    shutil.rmtree(f"/tmp/{extraction_path}")
                    raise HTTPException(status_code=401, detail="Extraction aborted! uncompressed size exceeds maximum allowed ratio.")

                tar.extract(member, path=f"/tmp/{extraction_path}/", filter="data")
    except tarfile.ReadError:
        raise HTTPException(status_code="401", detail="Malformed SPM package file, ensure it is TAR archived correctly, with a .spm extension.")



    validation = validate(f"/tmp/{extraction_path}/")
    if type(validation) == list:
        raise HTTPException(status_code=401, detail=f"Package definition is missing the following file(s)/directories: {validation}")

    with open(f"/tmp/{extraction_path}/meta.msgpack", "rb") as f:
        file_bytes = f.read()
        try:
            metadata = msgpack.unpackb(file_bytes, raw=False)
        except msgpack.ExtraData as e:
            raise HTTPException(status_code=401, detail=f"Invalid metadata: {e}")
        except (msgpack.UnpackValueError, ValueError, TypeError) as e:
            raise HTTPException(status_code=401, detail=f"Invalid metadata: {e}")
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid metadata: {e}")
        if not metadata["package_name"]:
            raise HTTPException(status_code=404, detail=f"No package name is declared in meta.msgpack!")
        if validation.stem != metadata["package_name"]:
            raise HTTPException(status_code=401, detail=f"Package name at 'src/{validation}' does not match metadata's declared package name '{metadata["package_name"]}'")

    security = security_check(f"/tmp/{extraction_path}")
    if not security[0]:
        raise HTTPException(status_code=401, detail=f"Security error {security[1]}")

    # compress src
    with tarfile.open(f"/tmp/{extraction_path}/src.tar.gz", "w:gz") as tar:
        tar.add(f"/tmp/{extraction_path}/src", arcname=os.path.basename(f"/tmp/{extraction_path}/src"))
    
    blob_upload(metadata["package_name"], f"/tmp/{extraction_path}")

        
                