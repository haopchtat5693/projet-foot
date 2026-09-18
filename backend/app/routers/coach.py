from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin
from app.services.coach_service import (
    search_coaches_by_name,
    sync_and_save_coach,
    sync_and_save_coaches_by_team,
)

router = APIRouter(prefix="/coaches", tags=["Coaches"])


@router.post("/", response_model=schemas.Coach)
def create_coach(
    coach: schemas.CoachCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.coach_crud.create_coach(db, coach)


@router.get("/search/", response_model=list[schemas.Coach])
async def search_coaches(
    name: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return await search_coaches_by_name(db, name=name)


@router.get("/team/{team_id}/", response_model=list[schemas.Coach])
async def get_coaches_by_team(team_id: int, db: Session = Depends(get_db)):
    try:
        coaches = await sync_and_save_coaches_by_team(db, team_id=team_id)
    except Exception as e:
        coaches = crud.coach_crud.get_coaches_by_team(db, team_id=team_id)
        if not coaches:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coaches non trouvés en base et échec de synchronisation API : {str(e)}",
            )

    if not coaches:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Coaches introuvables"
        )

    return coaches


@router.get("/{coach_id}/", response_model=schemas.Coach)
async def get_coach(coach_id: int, db: Session = Depends(get_db)):
    try:
        coach = await sync_and_save_coach(db, coach_id=coach_id)
    except Exception as e:
        coach = crud.coach_crud.get_coach(db, coach_id)
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coach non trouvé en base et échec de synchronisation API : {str(e)}",
            )

    if not coach:
        raise HTTPException(status_code=404, detail="Coach introuvable")

    return coach


@router.get("/", response_model=list[schemas.Coach])
async def get_coaches(
    team: int | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    if team is not None:
        return await sync_and_save_coaches_by_team(db, team_id=team)

    if search is not None:
        return await search_coaches_by_name(db, name=search)

    return crud.coach_crud.get_coaches(db)


@router.put("/{coach_id}/", response_model=schemas.Coach)
def update_coach(
    coach_id: int, 
    coach_in: schemas.CoachUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    coach = crud.coach_crud.get_coach(db, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return crud.coach_crud.update_coach(db, coach_id, coach_in)


@router.delete("/{coach_id}/", response_model=schemas.Coach)
def delete_coach(
    coach_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    coach = crud.coach_crud.get_coach(db, coach_id)
    if not coach:
        raise HTTPException(status_code=404, detail="Coach not found")
    return crud.coach_crud.delete_coach(db, coach_id)
