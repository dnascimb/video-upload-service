from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas, database, s3_service
import os
from io import BytesIO
from fastapi.responses import JSONResponse
from botocore.exceptions import NoCredentialsError, EndpointConnectionError
from pathlib import Path

app = FastAPI()

# Dependency to get the database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/videos/", response_model=schemas.VideoResponse)
async def upload_video(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    try:
        # Read the file and get its size
        file_content = await file.read()
        file_size = len(file_content)
        file_key = f"{file.filename}"

        # Upload file to S3
        upload = s3_service.upload_to_s3(BytesIO(file_content), file_key)

        # Save video metadata to the database
        video = crud.create_video(db, schemas.VideoCreate(filename=file.filename, file_size=file_size, upload_path=upload.upload_path))

        return video
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

@app.get("/videos/{video_id}", response_model=schemas.VideoResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if video is None:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    return video
