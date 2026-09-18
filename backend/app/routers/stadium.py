from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin

router = APIRouter(prefix="/stadiums", tags=["Stadiums"])


@router.post("/", response_model=schemas.Stadium)
def create_stadium(
    stadium: schemas.StadiumCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.stadium.create_stadium(db, stadium)


@router.get("/{stadium_id}/", response_model=schemas.Stadium)
def get_stadium(stadium_id: int, db: Session = Depends(get_db)):
    stadium = crud.stadium_crud.get_stadium(db, stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return stadium


@router.get("/", response_model=list[schemas.Stadium])
def get_stadiums(db: Session = Depends(get_db)):
    return crud.stadium_crud.get_stadiums(db)


@router.put("/{stadium_id}/", response_model=schemas.Stadium)
def update_stadium(
    stadium_id: int, 
    stadium_in: schemas.StadiumUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    stadium = crud.stadium_crud.get_stadium(db, stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return crud.stadium_crud.update_stadium(db, stadium_id, stadium_in)


@router.delete("/{stadium_id}/", response_model=schemas.Stadium)
def delete_stadium(
    stadium_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    stadium = crud.stadium_crud.get_stadium(db, stadium_id)
    if not stadium:
        raise HTTPException(status_code=404, detail="Stadium not found")
    return crud.stadium_crud.delete_stadium(db, stadium_id)
