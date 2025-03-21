from pydantic import BaseModel
from datetime import datetime

class VideoCreate(BaseModel):
    filename: str
    file_size: int
    upload_path: str

class VideoResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_time: datetime
    s3_url: str

    class Config:
        from_attributes = True
