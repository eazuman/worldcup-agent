// Predict game client — calls the backend champion-prediction endpoints.
// POST /predict/play compares the user's free-text guess to the agent's pick.

const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE) ||
  'http://localhost:8000'

export interface PredictFactors {
  team: string
  flag: string
  titles: number
  goals: number
  star: string | null
  star_goals: number
  score: number
}

export interface PlayResult {
  guess: string
  matched: string | null
  predicted: string
  win: boolean
  reasoning: string
  factors: PredictFactors
  leaderboard: PredictFactors[]
  source: 'live' | 'sample'
}

export async function playPrediction(guess: string): Promise<PlayResult> {
  const res = await fetch(`${API_BASE}/predict/play`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ guess }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
