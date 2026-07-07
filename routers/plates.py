from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import PlateRecord

router = APIRouter()


@router.get("/plates")
def get_all_plates(db: Session = Depends(get_db)):
    plates = db.query(PlateRecord).order_by(
        PlateRecord.scanned_at.desc()).all()
    return plates


@router.get("/plates/{plate_number}")
def search_plate(plate_number: str, db: Session = Depends(get_db)):
    results = db.query(PlateRecord).filter(
        PlateRecord.plate_number == plate_number.upper()
    ).all()
    if not results:
        raise HTTPException(status_code=404, detail="Plate not found")
    return results
