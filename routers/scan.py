from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import uuid
import os

from database import get_db
from models import PlateRecord
from services.ocr import extract_plate

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/scan")
async def scan_plate(image: UploadFile = File(...), db: Session = Depends(get_db)):

    ext = os.path.splitext(image.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    plate, debug_info = extract_plate(filepath)
    print("PLATE DETECTED:", debug_info)

    if not plate:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Could not read the plate clearly. Please retake the photo closer with good lighting.",
                "retake": True,
                "ocr_found": debug_info
            }
        )

    record = PlateRecord(
        plate_number=plate,
        image_path=filepath,
        scanned_at=datetime.utcnow()
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "plate_number": record.plate_number,
        "image_path": record.image_path,
        "scanned_at": record.scanned_at
    }
