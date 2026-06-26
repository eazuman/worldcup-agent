export type AnswerSource = 'rag' | 'live' | 'agent'

export interface AskResponse {
  answer: string
  source: AnswerSource
  tool: string
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  text: string
  source?: AnswerSource
  tool?: string
  pending?: boolean
}
