import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from a .env file

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")

settings = Settings()
