// PHASE 1 — MOCK football data for the Standings and Schedule views.
// Swapped for real football-data.org / MCP responses in Phases 4–6.
// World Cup 2026: 48 teams, 12 groups (A–L) of 4.

export interface TeamRow {
  team: string
  flag: string
  played: number
  won: number
  drawn: number
  lost: number
  gf: number
  ga: number
  points: number
}

export interface Group {
  name: string
  table: TeamRow[]
}

export interface Fixture {
  id: number
  date: string // ISO date
  time: string // UTC kickoff
  stage: string
  group?: string
  home: { team: string; flag: string }
  away: { team: string; flag: string }
  venue: string
  status: 'SCHEDULED' | 'LIVE' | 'FINISHED'
  score?: { home: number; away: number }
}

function row(
  team: string,
  flag: string,
  w: number,
  d: number,
  l: number,
  gf: number,
  ga: number,
): TeamRow {
  return { team, flag, played: w + d + l, won: w, drawn: d, lost: l, gf, ga, points: w * 3 + d }
}

export const GROUPS: Group[] = [
  {
    name: 'A',
    table: [
      row('Mexico', '🇲🇽', 2, 0, 0, 5, 1),
      row('Poland', '🇵🇱', 1, 1, 0, 3, 2),
      row('Saudi Arabia', '🇸🇦', 0, 1, 1, 1, 3),
      row('Norway', '🇳🇴', 0, 0, 2, 1, 4),
    ],
  },
  {
    name: 'B',
    table: [
      row('Canada', '🇨🇦', 2, 0, 0, 4, 1),
      row('Belgium', '🇧🇪', 1, 0, 1, 4, 3),
      row('Morocco', '🇲🇦', 1, 0, 1, 2, 2),
      row('Japan', '🇯🇵', 0, 0, 2, 1, 5),
    ],
  },
  {
    name: 'C',
    table: [
      row('USA', '🇺🇸', 2, 0, 0, 6, 2),
      row('Uruguay', '🇺🇾', 1, 1, 0, 4, 3),
      row('Ghana', '🇬🇭', 0, 1, 1, 2, 3),
      row('Australia', '🇦🇺', 0, 0, 2, 1, 5),
    ],
  },
  {
    name: 'D',
    table: [
      row('Argentina', '🇦🇷', 2, 0, 0, 5, 0),
      row('Croatia', '🇭🇷', 1, 0, 1, 3, 2),
      row('Nigeria', '🇳🇬', 1, 0, 1, 2, 3),
      row('Ecuador', '🇪🇨', 0, 0, 2, 0, 5),
    ],
  },
  {
    name: 'E',
    table: [
      row('France', '🇫🇷', 2, 0, 0, 6, 1),
      row('Senegal', '🇸🇳', 1, 0, 1, 3, 3),
      row('Denmark', '🇩🇰', 1, 0, 1, 2, 2),
      row('South Korea', '🇰🇷', 0, 0, 2, 1, 6),
    ],
  },
  {
    name: 'F',
    table: [
      row('Brazil', '🇧🇷', 2, 0, 0, 7, 1),
      row('Switzerland', '🇨🇭', 1, 1, 0, 3, 2),
      row('Cameroon', '🇨🇲', 0, 1, 1, 1, 3),
      row('Qatar', '🇶🇦', 0, 0, 2, 0, 5),
    ],
  },
  {
    name: 'G',
    table: [
      row('England', '🏴', 2, 0, 0, 5, 1),
      row('Netherlands', '🇳🇱', 1, 1, 0, 4, 2),
      row('Egypt', '🇪🇬', 0, 1, 1, 2, 4),
      row('Panama', '🇵🇦', 0, 0, 2, 1, 5),
    ],
  },
  {
    name: 'H',
    table: [
      row('Spain', '🇪🇸', 2, 0, 0, 6, 1),
      row('Colombia', '🇨🇴', 1, 1, 0, 3, 1),
      row('Iran', '🇮🇷', 0, 1, 1, 1, 3),
      row('New Zealand', '🇳🇿', 0, 0, 2, 0, 5),
    ],
  },
  {
    name: 'I',
    table: [
      row('Portugal', '🇵🇹', 2, 0, 0, 5, 2),
      row('Uruguay II', '🇺🇾', 1, 0, 1, 3, 3),
      row('Ivory Coast', '🇨🇮', 1, 0, 1, 2, 2),
      row('Jordan', '🇯🇴', 0, 0, 2, 1, 4),
    ],
  },
  {
    name: 'J',
    table: [
      row('Germany', '🇩🇪', 2, 0, 0, 6, 2),
      row('Italy', '🇮🇹', 1, 1, 0, 4, 2),
      row('Algeria', '🇩🇿', 0, 1, 1, 2, 4),
      row('Uzbekistan', '🇺🇿', 0, 0, 2, 1, 5),
    ],
  },
  {
    name: 'K',
    table: [
      row('Netherlands II', '🇳🇱', 2, 0, 0, 5, 1),
      row('Peru', '🇵🇪', 1, 0, 1, 2, 2),
      row('Tunisia', '🇹🇳', 1, 0, 1, 2, 3),
      row('South Africa', '🇿🇦', 0, 0, 2, 1, 4),
    ],
  },
  {
    name: 'L',
    table: [
      row('Croatia II', '🇭🇷', 2, 0, 0, 4, 1),
      row('Scotland', '🏴', 1, 1, 0, 3, 2),
      row('Paraguay', '🇵🇾', 0, 1, 1, 1, 2),
      row('Cape Verde', '🇨🇻', 0, 0, 2, 1, 4),
    ],
  },
]

export const FIXTURES: Fixture[] = [
  {
    id: 1,
    date: '2026-06-26',
    time: '16:00',
    stage: 'Group Stage · MD3',
    group: 'A',
    home: { team: 'Mexico', flag: '🇲🇽' },
    away: { team: 'Norway', flag: '🇳🇴' },
    venue: 'Estadio Azteca, Mexico City',
    status: 'LIVE',
    score: { home: 2, away: 0 },
  },
  {
    id: 2,
    date: '2026-06-26',
    time: '20:00',
    stage: 'Group Stage · MD3',
    group: 'C',
    home: { team: 'USA', flag: '🇺🇸' },
    away: { team: 'Australia', flag: '🇦🇺' },
    venue: 'MetLife Stadium, New Jersey',
    status: 'SCHEDULED',
  },
  {
    id: 3,
    date: '2026-06-27',
    time: '18:00',
    stage: 'Group Stage · MD3',
    group: 'D',
    home: { team: 'Argentina', flag: '🇦🇷' },
    away: { team: 'Ecuador', flag: '🇪🇨' },
    venue: 'SoFi Stadium, Los Angeles',
    status: 'SCHEDULED',
  },
  {
    id: 4,
    date: '2026-06-27',
    time: '21:00',
    stage: 'Group Stage · MD3',
    group: 'F',
    home: { team: 'Brazil', flag: '🇧🇷' },
    away: { team: 'Qatar', flag: '🇶🇦' },
    venue: 'AT&T Stadium, Dallas',
    status: 'SCHEDULED',
  },
  {
    id: 5,
    date: '2026-06-28',
    time: '17:00',
    stage: 'Group Stage · MD3',
    group: 'E',
    home: { team: 'France', flag: '🇫🇷' },
    away: { team: 'South Korea', flag: '🇰🇷' },
    venue: 'Lumen Field, Seattle',
    status: 'SCHEDULED',
  },
  {
    id: 6,
    date: '2026-06-28',
    time: '20:00',
    stage: 'Group Stage · MD3',
    group: 'G',
    home: { team: 'England', flag: '🏴' },
    away: { team: 'Panama', flag: '🇵🇦' },
    venue: 'Mercedes-Benz Stadium, Atlanta',
    status: 'SCHEDULED',
  },
  {
    id: 7,
    date: '2026-06-29',
    time: '19:00',
    stage: 'Group Stage · MD3',
    group: 'H',
    home: { team: 'Spain', flag: '🇪🇸' },
    away: { team: 'New Zealand', flag: '🇳🇿' },
    venue: 'Levi’s Stadium, San Francisco',
    status: 'SCHEDULED',
  },
  {
    id: 8,
    date: '2026-06-29',
    time: '22:00',
    stage: 'Group Stage · MD3',
    group: 'J',
    home: { team: 'Germany', flag: '🇩🇪' },
    away: { team: 'Uzbekistan', flag: '🇺🇿' },
    venue: 'Arrowhead Stadium, Kansas City',
    status: 'SCHEDULED',
  },
]
