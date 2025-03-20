from fastapi import FastAPI, HTTPException
from fastapi.exceptions import Exception

class InvalidFileFormatException(Exception):
    pass

class DatabaseError(Exception):
    pass

@app.exception_handler(InvalidFileFormatException)
async def file_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )

@app.exception_handler(DatabaseError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Database error occurred"},
    )