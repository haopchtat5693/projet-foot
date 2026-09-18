from fastapi import FastAPI

from app.routers import (
    coach,
    fixture,
    league,
    player,
    referee,
    season,
    stadium,
    team,
    users,
    auth,
    stats,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="FootballStats API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://projet-foot-seven.vercel.app",
                   "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(team.router)
app.include_router(league.router)
app.include_router(fixture.router)
app.include_router(player.router)
app.include_router(coach.router)
app.include_router(referee.router)
app.include_router(season.router)
app.include_router(stadium.router)
app.include_router(auth.router)
app.include_router(stats.router)
