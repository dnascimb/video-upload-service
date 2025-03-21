from sqlalchemy.orm import Session
from . import models, schemas

def create_video(db: Session, video: schemas.VideoCreate, s3_url: str):
    db_video = models.Video(
        filename=video.filename,
        file_size=video.file_size,
        s3_url=s3_url
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()
