from app.services.team_players_sync_service import sync_and_get_team_players_for_season
from app.services.team_service import search_teams_by_name
from app.services.team_sync_service import sync_and_save_team
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.post("/", response_model=schemas.Team)
def create_team(
    team: schemas.TeamCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.team_crud.create_team(db, team)


@router.get("/search/", response_model=list[schemas.Team])
async def search_teams(
    name: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return await search_teams_by_name(db, name=name)


@router.get("/{team_id}/", response_model=schemas.Team)
async def get_team(team_id: int, db: Session = Depends(get_db)):
    try:
        team = await sync_and_save_team(db, team_id=team_id)
    except Exception as e:
        team = crud.team_crud.get_team(db, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team non trouvée en base et échec de synchronisation API : {str(e)}",
            )

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team introuvable"
        )

    return team


@router.get(
    "/{team_id}/seasons/{season_id}/players/", response_model=list[schemas.Player]
)
async def get_team_players_for_season(
    team_id: int,
    season_id: int,
    db: Session = Depends(get_db),
):
    try:
        players = await sync_and_get_team_players_for_season(
            db, team_id=team_id, season_id=season_id
        )
    except Exception as e:
        players = crud.player_crud.get_players_by_team_and_season(
            db, team_id=team_id, season_id=season_id
        )
        if not players:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Players non trouvés en base et échec de synchronisation API : {str(e)}",
            )

    if not players:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Players introuvables"
        )

    return players


@router.get("/", response_model=list[schemas.Team])
def get_teams(db: Session = Depends(get_db)):
    return crud.team_crud.get_teams(db)


@router.put("/{team_id}/", response_model=schemas.Team)
def update_team(
    team_id: int, 
    team_in: schemas.TeamUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    team = crud.team_crud.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return crud.team_crud.update_team(db, team_id, team_in)


@router.delete("/{team_id}/", response_model=schemas.Team)
def delete_team(
    team_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    team = crud.team_crud.get_team(db, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return crud.team_crud.delete_team(db, team_id)
