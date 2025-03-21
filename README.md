Creating a FastAPI project that allows video uploads, stores them in an S3 bucket, and persists metadata in a database involves several components. Here's a step-by-step guide to building this project in a way that's scalable, efficient, and practical.

### Prerequisites:

- **Python 3.8+** (ensure it's installed on your Mac)
- **AWS S3** credentials (set up an S3 bucket)
- **PostgreSQL or any relational database** (locally using Docker or RDS on AWS)
- **FastAPI** for the API layer
- **SQLAlchemy** and **Alembic** for database interaction and migrations
- **Boto3** for S3 interaction
- **Pydantic** for data validation
- **Uvicorn** for development server
- **Docker** for local development setup

### Project Directory Structure:

```plaintext
video-upload-api/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── database.py
│   ├── main.py
│   ├── s3_service.py
│   └── config.py
├── alembic/
│   └── versions/
├── Dockerfile
├── requirements.txt
└── docker-compose.yml
```

### 1. Setting Up Dependencies

Start by creating a `requirements.txt` for your project:

```txt
fastapi
uvicorn
boto3
sqlalchemy
psycopg2
alembic
pydantic
python-dotenv
python-multipart
```

To install dependencies, run:

```bash
pip install -r requirements.txt
```

### 2. `config.py`: Configuration for Environment Variables

Create a `config.py` file where you can define configurations like database URI and S3 credentials. You can use `python-dotenv` to load `.env` variables.

```python
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
```

### 3. `database.py`: Database Setup (SQLAlchemy)

In this file, configure SQLAlchemy for connecting to your relational database (PostgreSQL in this case):

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 4. `models.py`: Define the Video Metadata Model

This file will define the structure of the database tables using SQLAlchemy. We'll create a `Video` model to store video metadata.

```python
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
```

### 5. `schemas.py`: Pydantic Models for Validation

Pydantic models are used to validate incoming requests. We'll define two models:

- `VideoCreate`: Used to validate video upload requests.
- `VideoResponse`: Used to format the response when querying for videos.

```python
from pydantic import BaseModel
from datetime import datetime

class VideoCreate(BaseModel):
    filename: str
    file_size: int

class VideoResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    upload_time: datetime
    s3_url: str

    class Config:
        orm_mode = True
```

### 6. `s3_service.py`: Handle S3 Uploads

In this file, use the `boto3` library to handle file uploads to AWS S3.

```python
import boto3
from botocore.exceptions import NoCredentialsError
from .config import settings

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

def upload_to_s3(file, bucket_name, file_key):
    try:
        s3_client.upload_fileobj(file, bucket_name, file_key)
        return f"s3://{bucket_name}/{file_key}"
    except NoCredentialsError:
        raise Exception("Credentials not available.")
```

### 7. `crud.py`: CRUD Operations for Videos

Here, define CRUD operations for interacting with the database.

```python
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
```

### 8. `main.py`: FastAPI Application

This file will set up the FastAPI application, including the route for uploading videos.

```python
from fastapi import FastAPI, File, UploadFile, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas, database, s3_service
import os
from io import BytesIO
from fastapi.responses import JSONResponse

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
        s3_url = s3_service.upload_to_s3(BytesIO(file_content), settings.S3_BUCKET_NAME, file_key)

        # Save video metadata to the database
        video = crud.create_video(db, schemas.VideoCreate(filename=file.filename, file_size=file_size), s3_url=s3_url)

        return video
    except Exception as e:
        return JSONResponse(status_code=400, content={"message": str(e)})

@app.get("/videos/{video_id}", response_model=schemas.VideoResponse)
async def get_video(video_id: int, db: Session = Depends(get_db)):
    video = crud.get_video(db, video_id)
    if video is None:
        return JSONResponse(status_code=404, content={"message": "Video not found"})
    return video
```

### 9. Local Development (Docker Setup)

**`docker-compose.yml`** for running the app with Docker locally:

```yaml
version: "3.8"
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: video_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/code
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

**`Dockerfile`** for setting up the FastAPI app container:

```dockerfile
FROM python:3.9-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 10. Running the App Locally

You can now run the application locally using Docker:

```bash
docker-compose up --build
```

Visit `http://localhost:8000/docs` to see the FastAPI docs and test the video upload.

### 11. Environment Variables (`.env`)

Create a `.env` file in the root directory for your sensitive configurations like database URL and AWS credentials.

```env
DATABASE_URL=postgresql://user:password@db:5432/video_db
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=your_region
```

### Scaling and AWS Setup

For horizontal scaling and production on AWS, consider deploying this app on:

- **Amazon ECS/Fargate** for container orchestration
- **RDS** for the relational database
- **AWS S3** for storing video files
- **AWS CloudWatch** for logging and monitoring

This setup ensures that the application is scalable and can handle video uploads efficiently both locally and in production.

