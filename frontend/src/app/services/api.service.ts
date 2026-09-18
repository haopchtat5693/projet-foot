import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { tap, shareReplay } from 'rxjs';
import type {
  League,
  LeagueLookupQuery,
  Stadium,
  Team,
  Season,
  Player,
  PlayerSeasonStats,
  TeamSeasonStats,
  Coach,
  Fixture,
} from '../interfaces/tables';

declare const APP_API_URL: string;

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = APP_API_URL;
  private readonly teamCache = new Map<number, Observable<Team>>();

  getTeams(): Observable<Team[]> {
    return this.http.get<Team[]>(`${this.apiUrl}/teams/`);
  }

  getTeamById(teamId: number): Observable<Team> {
    if (!this.teamCache.has(teamId)) {
      this.teamCache.set(
        teamId,
        this.http.get<Team>(`${this.apiUrl}/teams/${teamId}/`).pipe(shareReplay(1))
      );
    }
    return this.teamCache.get(teamId)!;
  }

  searchTeamsByName(name: string): Observable<Team[]> {
    const params = new URLSearchParams({ name });

    return this.http.get<Team[]>(`${this.apiUrl}/teams/search/?${params.toString()}`);
  }

  getSeasons(): Observable<Season[]> {
    return this.http.get<Season[]>(`${this.apiUrl}/seasons/`);
  }

  getStadiums(): Observable<Stadium[]> {
    return this.http.get<Stadium[]>(`${this.apiUrl}/stadiums/`);
  }

  getStadiumById(stadiumId: number): Observable<Stadium> {
    return this.http.get<Stadium>(`${this.apiUrl}/stadiums/${stadiumId}/`);
  }

  getLeagues(): Observable<League[]> {
    return this.http.get<League[]>(`${this.apiUrl}/leagues/`);
  }

  getLeagueById(leagueId: number): Observable<League> {
    return this.http.get<League>(`${this.apiUrl}/leagues/${leagueId}/`);
  }

  searchLeaguesByName(name: string): Observable<League[]> {
    return this.lookupLeagues({ search: name });
  }

  lookupLeagues(query: LeagueLookupQuery): Observable<League[]> {
    const params = new URLSearchParams();

    Object.entries(query).forEach(([key, value]) => {
      if (value === null || value === undefined || value === '') {
        return;
      }

      params.set(key, String(value));
    });

    const queryString = params.toString();
    const suffix = queryString ? `?${queryString}` : '';

    return this.http.get<League[]>(`${this.apiUrl}/leagues/lookup/${suffix}`);
  }

  getTeamPlayersForSeason(teamId: number, seasonId: number): Observable<Player[]> {
    return this.http.get<Player[]>(`${this.apiUrl}/teams/${teamId}/seasons/${seasonId}/players/`);
  }

  getTeamSeasonStats(teamId: number, leagueId: number, seasonId: number): Observable<TeamSeasonStats> {
    return this.http.get<TeamSeasonStats>(
      `${this.apiUrl}/stats/team/${teamId}/league/${leagueId}/season/${seasonId}/`,
    );
  }

  getPlayers(): Observable<Player[]> {
    return this.http.get<Player[]>(`${this.apiUrl}/players/`);
  }

  getPlayerById(playerId: number): Observable<Player> {
    return this.http.get<Player>(`${this.apiUrl}/players/${playerId}/`);
  }

  searchPlayersByName(
    name: string,
  ): Observable<Player[]> {
    const params = new URLSearchParams({ name });

    return this.http.get<Player[]>(`${this.apiUrl}/players/search/?${params.toString()}`);
  }

  getPlayerSeasonStats(playerId: number, seasonId: number): Observable<PlayerSeasonStats> {
    return this.http.get<PlayerSeasonStats>(`${this.apiUrl}/stats/player/${playerId}/season/${seasonId}/`);
  }

  getCoaches(): Observable<Coach[]> {
    return this.http.get<Coach[]>(`${this.apiUrl}/coaches/`);
  }

  getCoachById(coachId: number): Observable<Coach> {
    return this.http.get<Coach>(`${this.apiUrl}/coaches/${coachId}/`);
  }

  searchCoachesByName(name: string): Observable<Coach[]> {
    const params = new URLSearchParams({ name });

    return this.http.get<Coach[]>(`${this.apiUrl}/coaches/search/?${params.toString()}`);
  }

  getFixtures(): Observable<Fixture[]> {
    return this.http.get<Fixture[]>(`${this.apiUrl}/fixtures/`);
  }

  getFixtureById(fixtureId: number): Observable<Fixture> {
    return this.http.get<Fixture>(`${this.apiUrl}/fixtures/${fixtureId}/`);
  }

  getFixtureStatistics(fixtureId: number): Observable<Record<string, unknown>> {
    return this.http.get<Record<string, unknown>>(`${this.apiUrl}/fixtures/${fixtureId}/statistics/`);
  }

  getFixturesByLeague(leagueId: number, seasonId: number): Observable<Fixture[]> {
    const params = new URLSearchParams({ league_id: String(leagueId), season_id: String(seasonId) });
    const url = `${this.apiUrl}/fixtures/?${params.toString()}`;
    console.log('[ApiService] GET fixtures by league:', url);
    return this.http.get<Fixture[]>(url);
  }

  getFixturesByTeam(teamId: number): Observable<Fixture[]> {
    const params = new URLSearchParams({ team_id: String(teamId) });
    return this.http.get<Fixture[]>(`${this.apiUrl}/fixtures/?${params.toString()}`);
  }

  getFixturesByTeamAndSeason(teamId: number, seasonId: number, leagueId?: number): Observable<Fixture[]> {
    const params = new URLSearchParams({ team_id: String(teamId), season_id: String(seasonId) });
    if (leagueId) {
      params.append('league_id', String(leagueId));
    }
    const url = `${this.apiUrl}/fixtures/?${params.toString()}`;
    console.log('[ApiService] GET fixtures by team and season:', { teamId, seasonId, leagueId, url });
    return this.http.get<Fixture[]>(url).pipe(
      tap((fixtures) => {
        console.log('[ApiService] Fixtures response:', { count: fixtures.length, teamId, seasonId, leagueId });
        fixtures.forEach((f, idx) => {
          console.log(`  [${idx}] Fixture ID=${f.id}, home_team=${f.home_team_id}, away_team=${f.away_team_id}, league=${f.league_id}, season=${f.season_id}`);
        });
      })
    );
  }

  getFixturesByDate(date: string): Observable<Fixture[]> {
    const params = new URLSearchParams({ date });
    return this.http.get<Fixture[]>(`${this.apiUrl}/fixtures/?${params.toString()}`);
  }
}