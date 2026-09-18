from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin
from app.services.player_service import search_players_by_name

router = APIRouter(prefix="/players", tags=["Players"])


@router.post("/", response_model=schemas.Player)
def create_player(
    player: schemas.PlayerCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.player_crud.create_player(db, player)


@router.get("/search/", response_model=list[schemas.Player])
async def search_players(
    name: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return await search_players_by_name(
        db,
        name=name,
    )


@router.get("/{player_id}/", response_model=schemas.Player)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = crud.player_crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/", response_model=list[schemas.Player])
def get_players(db: Session = Depends(get_db)):
    return crud.player_crud.get_players(db)


@router.put("/{player_id}/", response_model=schemas.Player)
def update_player(
    player_id: int, 
    player_in: schemas.PlayerUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    player = crud.player_crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return crud.player_crud.update_player(db, player_id, player_in)


@router.delete("/{player_id}/", response_model=schemas.Player)
def delete_player(
    player_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    player = crud.player_crud.get_player(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return crud.player_crud.delete_player(db, player_id)
