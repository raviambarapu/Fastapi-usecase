import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter,File,HTTPException, UploadFile, status

from typing import Annotated

from fastapi.responses import FileResponse

router = APIRouter(prefix="/uploads", tags=["File Uploads"])

UPLOAD_DIR = Path("uploads")

MAX_SIZE = 5*1024*1024 # 5MB

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/plain",
}

ALLOWED_EXTENSIONS = {
    ".jpeg",
    ".jpg",
    ".png",
    "webp",
    ".pdf",
    ".txt",
}

UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

def safe_filename(original:str) -> str:

    extension = Path(original).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Extension not allowed: {extension}")

    return f"{uuid.uuid4()}{extension}"


# for single file upload
@router.post("/single",status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):

    # validate MIME type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,detail=f"Unsupported file type: {file.content_type}")

    # Generate filename
    filename = safe_filename(file.filename or "upload.bin")
    destination = UPLOAD_DIR/filename


    # Stream file to disk
    total = 0

    try:

        async with aiofiles.open(destination, "wb") as output:

            while chunk := await file.read(64 * 1024):

                total += len(chunk)

                if total > MAX_SIZE:
                    await output.close()

                    destination.unlink(missing_ok=True)

                    raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=(
                        "File too large."
                        "Maximum size is 5MB."
                        ))

                await output.write(chunk)

    finally:
        await file.close()

    return {
        "filename": filename,
        "original_filname": file.filename,
        "size_bytes": total,
        "content_type": file.content_type,
    }

# for multi file uploads
@router.post("/multiple")
async def upload_multiple(files: Annotated[list[UploadFile], File()]):

    if not files:
        raise HTTPException(status_code=400, detail="No files received")

    if len(files) > 10:
        raise HTTPException(status_code=400,detail="Maximu 10 files per request")

    results = []

    for file in files:

        if file.content_type not in ALLOWED_TYPES:

            results.append({
                "filename": file.filename,
                "error": "Unsupported file type"
            })

            continue

        filename = safe_filename(file.filename or "upload")

        destination = UPLOAD_DIR/filename

        content = await file.read()

        if len(content) > MAX_SIZE:

            results.append({
                "filename": file.filename,
                "error": "File too large"
            })

            continue

        async with aiofiles.open(destination,"wb") as output:

            await output.write(content)

        results.append({
            "filename":file.filename,
            "size": len(content)
        })

        await file.close()

    return {"uploaded":results}



# File download 
@router.get("/download/{filename}")
async def download_file(filename:str):

    safe_name = Path(filename).name # removing the parents dir

    file_path = UPLOAD_DIR/safe_name

    if not file_path.exists():
        raise HTTPException(status_code=404,detail="File not found")

    if not file_path.is_file():
        raise HTTPException(status_code=404,detail="File not found")

    return FileResponse(path=file_path,filename=safe_name,media_type="application/octet-stream")
