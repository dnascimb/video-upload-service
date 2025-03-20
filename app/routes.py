from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from app.models import User, Video
from app.schemas import VideoSchema, UploadResponse
from sqlalchemy.orm import Session
import os

app = FastAPI()

# Database session setup (add this to your actual project with proper configuration)
# This is just a placeholder for demonstration.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/videos", response_model=List[VideoSchema])
def get_all_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return videos

@app.post("/upload", response_model=UploadResponse)
def upload_video(
    video_data: dict,
    db: Session = Depends(get_db),
    api_key: str = Header(...)
):
    try:
        # Validate API key and get uploader
        user = db.query(User).filter(User.api_key == api_key).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )

        video = Video(**video_data, uploader_id=user.id)
        db.add(video)
        db.commit()

        return {"success": True, "message": "Video uploaded successfully", "video_id": video.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@app.get("/search")
def search_videos(query: str, db: Session = Depends(get_db)):
    try:
        videos = (
            db.query(Video)
            .filter(
                Video.title.ilike(f"%{query}%")
                | Video.description.ilike(f"%{query}%")
            )
            .all()
        )
        return [VideoSchema.from_orm(video) for video in videos]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)