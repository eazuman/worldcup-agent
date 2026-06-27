// Fetches structured standings & schedule from the backend (/standings, /schedule).
// The backend returns source:'live' when an API key is configured, otherwise
// source:'sample' with empty data — in which case we fall back to the built-in
// sample dataset so the views always render.

import { GROUPS, FIXTURES, type Group, type Fixture } from './footballMock'

const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE) ||
  'http://localhost:8000'

export interface StandingsResult {
  source: 'live' | 'sample'
  groups: Group[]
}

export interface ScheduleResult {
  source: 'live' | 'sample'
  fixtures: Fixture[]
}

export async function fetchStandings(): Promise<StandingsResult> {
  try {
    const res = await fetch(`${API_BASE}/standings`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (data.source === 'live' && Array.isArray(data.groups) && data.groups.length) {
      return { source: 'live', groups: data.groups }
    }
  } catch {
    /* fall through to sample */
  }
  return { source: 'sample', groups: GROUPS }
}

export async function fetchSchedule(): Promise<ScheduleResult> {
  try {
    const res = await fetch(`${API_BASE}/schedule`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    if (data.source === 'live' && Array.isArray(data.fixtures) && data.fixtures.length) {
      return { source: 'live', fixtures: data.fixtures }
    }
  } catch {
    /* fall through to sample */
  }
  return { source: 'sample', fixtures: FIXTURES }
}

// Overall data mode shown in the header badge: 'live' if EITHER standings or
// schedule is served from a real API, otherwise 'sample' (built-in mock data).
export async function fetchDataMode(): Promise<'live' | 'sample'> {
  const [standings, schedule] = await Promise.all([fetchStandings(), fetchSchedule()])
  return standings.source === 'live' || schedule.source === 'live' ? 'live' : 'sample'
}
