import type { AskResponse, AnswerSource } from './types'

// PHASE 1 — MOCK ONLY.
// This fakes the future backend `POST /ask` so we can build and ship the UI first.
// In Phase 6 this file is swapped for a real fetch() to the FastAPI backend; the UI
// and the AskResponse shape stay identical.

const LIVE_WORDS = [
  'today', 'score', 'scores', 'standing', 'standings', 'table', 'fixture', 'fixtures',
  'next', 'live', 'scorer', 'scorers', 'group', 'result', 'results', 'playing', 'play',
  'kickoff', 'lineup', 'tonight',
]

const RAG_WORDS = [
  'history', 'format', 'won', 'winner', 'most', 'stadium', 'rule', 'rules', 'past',
  'record', 'records', '1930', '2022', 'profile', 'host', 'hosts', 'explain',
]

export function classify(question: string): AnswerSource {
  const t = question.toLowerCase()
  const live = LIVE_WORDS.some((w) => t.includes(w))
  const rag = RAG_WORDS.some((w) => t.includes(w))
  if (live && rag) return 'agent'
  if (live) return 'live'
  if (rag) return 'rag'
  return 'agent'
}

const CANNED: Record<AnswerSource, { tool: string; reply: string }> = {
  live: {
    tool: 'get_fixtures · MCP → football-data.org',
    reply:
      '🔴 [MOCK LIVE] Example: “USA vs Mexico kicks off today at 20:00 UTC, Group D.” ' +
      'This is dummy data — Phase 4 wires the real MCP football tools.',
  },
  rag: {
    tool: 'rag_search · Chroma',
    reply:
      '📚 [MOCK RAG] Example: “The 2026 World Cup expands to 48 teams in 12 groups of four.” ' +
      'This is dummy data — Phase 3 wires the real RAG corpus.',
  },
  agent: {
    tool: 'agent · RAG + live',
    reply:
      '🧠 [MOCK AGENT] I would combine historical context (RAG) with live data (MCP) to answer this. ' +
      'This is dummy data — Phase 5 wires the real agent.',
  },
  mcp: {
    tool: 'get_live_scores · MCP → football-data.org',
    reply:
      '🛰️ [MOCK MCP] Live scores, standings and fixtures come from the MCP football server. ' +
      'This is dummy data — Phase 4 wires the real MCP football tools.',
  },
}

export async function askMock(question: string): Promise<AskResponse> {
  // Simulate network + model latency.
  await new Promise((r) => setTimeout(r, 600))
  const source = classify(question)
  const c = CANNED[source]
  return { answer: c.reply, source, tool: c.tool }
}

export const SAMPLE_QUESTIONS = [
  'Which country has won the most World Cups?',
  'How is the GoldenGoal agent set up — walk me through how it works?',
  'What World Cup matches are on the schedule today?',
  'As a coach, how would an underdog beat a stronger team?',
]

// Which agent workflow each sample question is designed to showcase. Shown as a
// hint just before the agent answers so the routing is visible in the demo.
export const SAMPLE_WORKFLOW_NOTES: Record<string, string> = {
  'Which country has won the most World Cups?':
    '📚 This response uses the RAG workflow — answered from the World Cup knowledge base.',
  'How is the GoldenGoal agent set up — walk me through how it works?':
    '🧩 This response uses the skill workflow — the agent reads its own architecture docs.',
  'What World Cup matches are on the schedule today?':
    '🛰️ This response uses the MCP workflow — live data from the football tools.',
  'As a coach, how would an underdog beat a stronger team?':
    '🧠 This response uses LLM reasoning — the coach answers from its own football expertise, no tool needed.',
}
