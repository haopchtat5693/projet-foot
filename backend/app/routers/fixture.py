from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.core.deps import get_current_manager, get_current_admin
from app.services.fixture_sync_service import (
    sync_and_save_fixture,
    sync_fixture_statistics,
    sync_fixtures_by_league,
    sync_fixtures_by_team,
)

router = APIRouter(prefix="/fixtures", tags=["Fixtures"])


@router.post("/", response_model=schemas.Fixture)
def create_fixture(
    fixture: schemas.FixtureCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    return crud.fixture_crud.create_fixture(db, fixture)


@router.get("/{fixture_id}/", response_model=schemas.Fixture)
async def get_fixture(fixture_id: int, db: Session = Depends(get_db)):
    print(f"[ROUTER] GET /fixtures/{fixture_id}")
    
    fixture = crud.fixture_crud.get_fixture(db, fixture_id)
    if fixture:
        print(f"[ROUTER] Found in DB - fixture ID={fixture_id}: home_team={fixture.home_team_id}, away_team={fixture.away_team_id}")
        return fixture
    
    print(f"[ROUTER] Not in DB, syncing from API for fixture_id={fixture_id}")
    try:
        fixture = await sync_and_save_fixture(db, fixture_id=fixture_id)
        print(f"[ROUTER] Synced fixture ID={fixture_id}: home_team={fixture.home_team_id if fixture else None}, away_team={fixture.away_team_id if fixture else None}")
    except Exception as e:
        print(f"[ROUTER] Error syncing fixture {fixture_id}: {str(e)}")
        if not fixture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fixture not found in database or API: {str(e)}",
            )

    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Fixture not found"
        )

    return fixture


@router.get("/{fixture_id}/statistics/", response_model=dict)
async def get_fixture_statistics(fixture_id: int, db: Session = Depends(get_db)):
    try:
        fixture = await sync_fixture_statistics(db, fixture_id)
        if fixture and fixture.statistics:
            return fixture.statistics
    except Exception:
        pass

    statistics = crud.fixture_crud.get_fixture_statistics(db, fixture_id)
    if statistics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Statistics not found for this fixture",
        )
    return statistics


@router.get("/", response_model=list[schemas.Fixture])
async def get_fixtures(
    league_id: int = Query(None),
    season_id: int = Query(None),
    team_id: int = Query(None),
    date: str = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):

    if team_id:
        try:
            print(f"[ROUTER] Getting fixtures for team_id={team_id}")
            fixtures = await sync_fixtures_by_team(db, team_id, season_id, league_id)
            print(f"[ROUTER] Got {len(fixtures)} fixtures for team_id={team_id}")
            if fixtures:
                print(f"[ROUTER] First fixture: id={fixtures[0].id}, home_goals={fixtures[0].home_goals}, away_goals={fixtures[0].away_goals}")
            return fixtures
        except Exception as e:
            print(f"[ROUTER] Error syncing team fixtures: {str(e)}")
            pass

    if league_id and season_id:
        try:
            return await sync_fixtures_by_league(db, league_id, season_id)
        except Exception:
            pass

    print(f"[ROUTER] Fallback to CRUD queries: league_id={league_id}, season_id={season_id}, team_id={team_id}, date={date}")
    if league_id and season_id:
        print(f"[ROUTER] Using get_fixtures_by_league_and_season: league_id={league_id}, season_id={season_id}")
        return crud.fixture_crud.get_fixtures_by_league_and_season(db, league_id, season_id, skip, limit)
    if league_id:
        print(f"[ROUTER] Using get_fixtures_by_league: league_id={league_id}")
        return crud.fixture_crud.get_fixtures_by_league(db, league_id, skip, limit)
    if team_id and season_id:
        print(f"[ROUTER] Using get_fixtures_by_team_league_and_season: team_id={team_id}, season_id={season_id}, league_id={league_id}")
        return crud.fixture_crud.get_fixtures_by_team_league_and_season(db, team_id, season_id, league_id, skip, limit)
    if team_id:
        print(f"[ROUTER] Using get_fixtures_by_team: team_id={team_id}")
        return crud.fixture_crud.get_fixtures_by_team(db, team_id, skip, limit)
    if date:
        print(f"[ROUTER] Using get_fixtures_by_date: date={date}")
        return crud.fixture_crud.get_fixtures_by_date(db, date, skip, limit)

    print("[ROUTER] Using get_all_fixtures")
    return crud.fixture_crud.get_fixtures(db, skip, limit)


@router.put("/{fixture_id}/", response_model=schemas.Fixture)
def update_fixture(
    fixture_id: int, 
    fixture_in: schemas.FixtureUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_manager),
):
    fixture = crud.fixture_crud.get_fixture(db, fixture_id)
    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return crud.fixture_crud.update_fixture(db, fixture_id, fixture_in)


@router.delete("/{fixture_id}/", response_model=schemas.Fixture)
def delete_fixture(
    fixture_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    fixture = crud.fixture_crud.get_fixture(db, fixture_id)
    if not fixture:
        raise HTTPException(status_code=404, detail="Fixture not found")
    return crud.fixture_crud.delete_fixture(db, fixture_id)
