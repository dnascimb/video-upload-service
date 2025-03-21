from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Video(Base):
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.utcnow)
    s3_url = Column(String)

    def __repr__(self):
        return f"Video(id={self.id}, filename={self.filename}, s3_url={self.s3_url})"
