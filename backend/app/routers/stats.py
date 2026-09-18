from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.services.stats_sync_service import (
    sync_and_save_season_stats,
    sync_and_save_team_stats,
)

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get(
    "/player/{player_id}/season/{season_id}/", response_model=schemas.PlayerSeasonStats
)
async def get_player_stats_for_season(
    player_id: int, season_id: int, db: Session = Depends(get_db)
):
    stats = crud.player_season_stats_crud.get_season_stats_by_player_and_season(
        db, player_id=player_id, season_id=season_id
    )

    if not stats:
        try:
            stats = await sync_and_save_season_stats(
                db, player_id=player_id, season_id=season_id
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stats non trouvées en base et échec de synchronisation API : {str(e)}",
            )

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Stats introuvables"
        )

    return stats


@router.get(
    "/team/{team_id}/league/{league_id}/season/{season_id}/",
    response_model=schemas.TeamSeasonStats,
)
async def get_team_stats_for_team_league_season(
    team_id: int,
    league_id: int,
    season_id: int,
    db: Session = Depends(get_db),
):
    try:
        stats = await sync_and_save_team_stats(
            db,
            team_id=team_id,
            league_id=league_id,
            season_id=season_id,
        )
    except Exception as e:
        stats = (
            crud.team_season_stats_crud.get_team_season_stats_by_team_league_and_season(
                db,
                team_id=team_id,
                league_id=league_id,
                season_id=season_id,
            )
        )

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team stats non trouvées en base et échec de synchronisation API : {str(e)}",
            )

    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team stats introuvables"
        )

    return stats
