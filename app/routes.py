from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.models.database import SessionLocal
from app.models.entities import Vehicle


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class VehicleCreate(BaseModel):
    registration: str
    brand: str
    model: str
    status: str = "available"


class VehicleRead(VehicleCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


@router.get("/vehicles", response_model=list[VehicleRead])
def list_vehicles(db: Session = Depends(get_db)):
    return db.query(Vehicle).order_by(Vehicle.id).all()


@router.get("/vehicles/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
):
    vehicle = db.get(Vehicle, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    return vehicle


@router.post(
    "/vehicles",
    response_model=VehicleRead,
    status_code=201,
)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
):
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)

    try:
        db.commit()
        db.refresh(vehicle)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Could not create vehicle; check unique registration",
        )

    return vehicle
