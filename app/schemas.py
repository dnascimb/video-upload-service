from pydantic import BaseModel

class VideoSchema(BaseModel):
    id: int
    title: str
    description: str | None
    upload_date: str
    duration: int | None
    uploader_id: int

    class Config:
        orm_mode = True

class UploadResponse(BaseModel):
    success: bool
    message: str
    video_id: int | None