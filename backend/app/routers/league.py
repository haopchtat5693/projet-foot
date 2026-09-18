from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin
from app.services.league_service import lookup_leagues as lookup_leagues_service

router = APIRouter(prefix="/leagues", tags=["Leagues"])


@router.get("/lookup/")
async def lookup_leagues_route(
    db: Session = Depends(get_db),
    league_id: int | None = Query(None, alias="id"),
    search: str | None = Query(None),
    season: int | None = Query(None),
    team_id: int | None = Query(None, alias="team"),
    league_type: str | None = Query(None, alias="type"),
) -> list[schemas.League]:
    return await lookup_leagues_service(
        db=db,
        league_id=league_id,
        search=search,
        season=season,
        team_id=team_id,
        league_type=league_type,
    )


@router.post("/", response_model=schemas.League)
def create_league(
    league: schemas.LeagueCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.league_crud.create_league(db, league)


@router.get("/{league_id}/", response_model=schemas.League)
def get_league(league_id: int, db: Session = Depends(get_db)):
    league = crud.league_crud.get_league(db, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return league


@router.get("/", response_model=list[schemas.League])
def get_leagues(db: Session = Depends(get_db)):
    return crud.league_crud.get_leagues(db)


@router.put("/{league_id}/", response_model=schemas.League)
def update_league(
    league_id: int, 
    league_in: schemas.LeagueUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    league = crud.league_crud.get_league(db, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return crud.league_crud.update_league(db, league_id, league_in)


@router.delete("/{league_id}/", response_model=schemas.League)
def delete_league(
    league_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    league = crud.league_crud.get_league(db, league_id)
    if not league:
        raise HTTPException(status_code=404, detail="League not found")
    return crud.league_crud.delete_league(db, league_id)
