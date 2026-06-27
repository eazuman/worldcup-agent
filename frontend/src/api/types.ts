export type AnswerSource = 'rag' | 'live' | 'agent' | 'mcp'

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
  // When true the message is rendered as a subtle centered hint (not a bubble),
  // used to show which agent workflow a sample question demonstrates.
  note?: boolean
}
