import { describe, it, expect } from 'vitest'
import {
  askMock,
  classify,
  SAMPLE_QUESTIONS,
  SAMPLE_WORKFLOW_NOTES,
} from './mock'

describe('classify', () => {
  it('routes live keywords to the live source', () => {
    expect(classify('What is the score today?')).toBe('live')
    expect(classify('Show me the standings')).toBe('live')
  })

  it('routes reference keywords to the rag source', () => {
    expect(classify('Who won the most World Cups in history?')).toBe('rag')
    expect(classify('Explain the tournament format')).toBe('rag')
  })

  it('routes mixed live + reference questions to the agent', () => {
    expect(classify("Compare today's standings to their 1930 World Cup history")).toBe('agent')
  })

  it('falls back to the agent for everything else', () => {
    expect(classify('Tell me about football')).toBe('agent')
  })
})

describe('sample questions', () => {
  it('exposes four predefined questions', () => {
    expect(SAMPLE_QUESTIONS).toHaveLength(4)
  })

  it('has a workflow note for every sample question', () => {
    for (const q of SAMPLE_QUESTIONS) {
      expect(SAMPLE_WORKFLOW_NOTES[q]).toBeTruthy()
    }
  })
})

describe('askMock', () => {
  it('returns an answer, source and tool', async () => {
    const res = await askMock('Who won the most World Cups?')
    expect(res.source).toBe('rag')
    expect(res.answer).toBeTruthy()
    expect(res.tool).toBeTruthy()
  })
})
