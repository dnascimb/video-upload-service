# FastAPI Video Upload API

This repository contains a FastAPI-based API for managing video uploads and searches.

## Prerequisites

- Python 3.8+
- pip
- PostgreSQL or SQLite database

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/video-upload-api.git
   cd video-upload-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your database configuration and API key secret:
   ```
   DATABASE_URL=sqlite:///./test.db  # or PostgreSQL URL
   API_KEY_SECRET=your-secret-key-here
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Endpoints

### Upload Video
- **POST /upload**
  - Requires an API key in the header.
  - Accepts video metadata (title, description, duration).

### Get All Videos
- **GET /videos**

### Search Videos
- **GET /search?q=QUERY**

## Configuration

Update `app/config.py` with your database URL and API key secret.

## Testing

Use tools like Postman or curl to test the API endpoints.