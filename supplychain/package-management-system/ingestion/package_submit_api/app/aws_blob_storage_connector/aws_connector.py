import boto3
import os

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")

def blob_upload(user, package_name, version, source):
    s3_client = boto3.client('s3', 
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='us-east-2')

    bucket = "simple-package-managerbucket"

    for filename in os.listdir(source):
            fullpath = os.path.join(source, filename)

            s3_key = f"{user}/{package_name}/{version}/{filename}.bin"

            try:
                s3_client.upload_file(fullpath, bucket, s3_key)

            except Exception as e:
                 print(f"Failed to upload {filename}: {e}")
            

    