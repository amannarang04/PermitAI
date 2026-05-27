import os
import boto3
from botocore.exceptions import ClientError
from app.config import settings

class StorageService:
    @staticmethod
    def get_s3_client():
        if (settings.AWS_ACCESS_KEY_ID == "mock" or 
            settings.AWS_ACCESS_KEY_ID == "your-access-key" or 
            not settings.AWS_ACCESS_KEY_ID or 
            settings.AWS_ACCESS_KEY_ID.startswith("your-")):
            return None
        try:
            return boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception:
            return None

    @staticmethod
    async def upload_file(file_content: bytes, file_name: str, application_id: str) -> str:
        s3 = StorageService.get_s3_client()
        key = f"{application_id}/{file_name}"
        
        if s3:
            try:
                s3.put_object(
                    Bucket=settings.S3_BUCKET_NAME,
                    Key=key,
                    Body=file_content
                )
                return f"s3://{settings.S3_BUCKET_NAME}/{key}"
            except ClientError:
                pass

        local_dir = os.path.join(os.getcwd(), "local_storage", application_id)
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, file_name)
        with open(local_path, "wb") as f:
            f.write(file_content)
        return local_path

    @staticmethod
    def download_file(file_path: str) -> bytes:
        if file_path.startswith("s3://"):
            s3 = StorageService.get_s3_client()
            if s3:
                parts = file_path.replace("s3://", "").split("/", 1)
                bucket = parts[0]
                key = parts[1]
                response = s3.get_object(Bucket=bucket, Key=key)
                return response["Body"].read()
        
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        
        rel_path = os.path.basename(file_path)
        local_root = os.path.join(os.getcwd(), "local_storage")
        if os.path.exists(local_root):
            for root, _, files in os.walk(local_root):
                if rel_path in files:
                    with open(os.path.join(root, rel_path), "rb") as f:
                        return f.read()
                        
        raise FileNotFoundError(f"File not found: {file_path}")
