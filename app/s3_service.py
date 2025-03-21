import boto3
import os
from botocore.exceptions import NoCredentialsError, EndpointConnectionError, InvalidRegionError
from .config import settings
from pathlib import Path
from .schemas import VideoCreate
import shutil
from .logging_config import logger

S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
LOCAL_STORAGE_DIR = os.getenv('LOCAL_STORAGE_DIR', './uploads')
s3_enabled = False
s3_client = None

Path(LOCAL_STORAGE_DIR).mkdir(parents=True, exist_ok=True)

# Try to initialize S3 client
try:
    if S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY and S3_BUCKET_NAME:
        s3_client = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY_ID,
                                 aws_secret_access_key=S3_SECRET_ACCESS_KEY)
        # Check if the connection is successful by trying to list the S3 bucket
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        s3_enabled = True
except (NoCredentialsError, EndpointConnectionError, InvalidRegionError) as e:
    print(f"S3 Connection Error: {e}")
    s3_enabled = False

def upload_to_s3(file, file_key):
    try:
        if not s3_enabled:
            # If S3 is not available, store the file locally
            file_location = os.path.join(LOCAL_STORAGE_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            metadata = VideoCreate(filename=file.filename, file_size=os.path.getsize(file_location), upload_path=file_location)
            return {"message": "File uploaded locally", "metadata": metadata.model_dump_json()}
    
        logger.info(f"Attempting to upload file {file.filename} to S3.")

        s3_client.upload_fileobj(file, S3_BUCKET_NAME, file_key)
        metadata = VideoCreate(filename=file, file_size=0, upload_path=f"s3://{S3_BUCKET_NAME}/{file_key}")
        return {"message": "File uploaded locally", "metadata": metadata.model_dump_json()}
    except NoCredentialsError:
        logger.error(f"Failed to upload file {file.filename}: {str(e)}")
        raise Exception("Credentials not available.")
