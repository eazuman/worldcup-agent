// Streaming client for the backend agent endpoint (POST /agent/chat).
// Parses Server-Sent Events and forwards token / tool / done / error frames.

const API_BASE =
  ((import.meta as unknown as { env?: Record<string, string> }).env?.VITE_API_BASE) ||
  'http://localhost:8000'

export interface AgentHandlers {
  onToken: (text: string) => void
  onTool?: (name: string, phase: 'start' | 'end') => void
  onDone?: () => void
  onError?: (detail: string) => void
}

export async function streamAgent(
  question: string,
  handlers: AgentHandlers,
  threadId = 'default',
): Promise<void> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, thread_id: threadId }),
    })
  } catch (err) {
    handlers.onError?.(`Could not reach the backend at ${API_BASE}. Is it running?`)
    return
  }

  if (!res.ok || !res.body) {
    handlers.onError?.(`Backend returned HTTP ${res.status}`)
    return
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finished = false

  const finish = () => {
    if (!finished) {
      finished = true
      handlers.onDone?.()
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // SSE frames are separated by a blank line.
    const frames = buffer.split('\n\n')
    buffer = frames.pop() ?? ''

    for (const frame of frames) {
      const line = frame.trim()
      if (!line.startsWith('data:')) continue
      const json = line.slice(5).trim()
      if (!json) continue

      let evt: { type: string; content?: string; name?: string; detail?: string }
      try {
        evt = JSON.parse(json)
      } catch {
        continue
      }

      switch (evt.type) {
        case 'token':
          handlers.onToken(evt.content ?? '')
          break
        case 'tool_start':
          handlers.onTool?.(evt.name ?? '', 'start')
          break
        case 'tool_end':
          handlers.onTool?.(evt.name ?? '', 'end')
          break
        case 'done':
          finish()
          break
        case 'error':
          handlers.onError?.(evt.detail ?? 'Unknown error')
          break
      }
    }
  }

  finish()
}
