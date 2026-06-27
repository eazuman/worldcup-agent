<script setup lang="ts">
import { nextTick, ref } from 'vue'
import MessageBubble from './MessageBubble.vue'
import { streamAgent } from '../api/agent'
import { SAMPLE_QUESTIONS, SAMPLE_WORKFLOW_NOTES } from '../api/mock'
import type { ChatMessage } from '../api/types'

const messages = ref<ChatMessage[]>([
  {
    id: 0,
    role: 'assistant',
    text:
      "Hey! I'm your World Cup soccer coach. Ask me about the 2026 tournament — " +
      "format, hosts, stadiums, team history — or about how this agent itself works.\n\n" +
      '📚 History & facts come from my knowledge base (RAG). ' +
      '🛰️ Live scores, standings & today’s schedule come from the MCP football server. ' +
      '🧩 Ask how I’m built and I’ll explain my own setup (architecture skill).',
    source: 'agent',
    tool: 'Coach · knowledge base',
  },
])
const input = ref('')
const busy = ref(false)
const scroller = ref<HTMLElement | null>(null)
let nextId = 1

async function scrollToBottom() {
  await nextTick()
  scroller.value?.scrollTo({ top: scroller.value.scrollHeight, behavior: 'smooth' })
}

async function send(text?: string) {
  const question = (text ?? input.value).trim()
  if (!question || busy.value) return

  input.value = ''
  busy.value = true

  messages.value.push({ id: nextId++, role: 'user', text: question })

  // For the predefined sample questions, show a hint of which agent workflow
  // (RAG / MCP / skill) the question is designed to demonstrate.
  const workflowNote = SAMPLE_WORKFLOW_NOTES[question]
  if (workflowNote) {
    messages.value.push({ id: nextId++, role: 'assistant', text: workflowNote, note: true })
  }

  // The backend agent decides which tool(s) to call — RAG for historical /
  // reference facts, MCP for live schedule / standings. The UI just streams
  // whatever the agent produces and shows the tool it actually used.
  const pendingId = nextId++
  messages.value.push({
    id: pendingId,
    role: 'assistant',
    text: '',
    pending: true,
    source: 'agent',
    tool: 'Coach · thinking…',
  })
  await scrollToBottom()

  const indexOfPending = () => messages.value.findIndex((m) => m.id === pendingId)
  const patch = (changes: Partial<ChatMessage>) => {
    const i = indexOfPending()
    if (i !== -1) messages.value[i] = { ...messages.value[i], ...changes }
  }

  let answer = ''

  await streamAgent(question, {
    onToken: (chunk) => {
      answer += chunk
      patch({ text: answer, pending: false })
      scrollToBottom()
    },
    onTool: (name, phase) => {
      // Show which capability the agent reached for. RAG = knowledge base,
      // the architecture skill = self/meta docs, anything else = a live-data
      // MCP football tool.
      if (phase === 'start') {
        const proto =
          name === 'search_worldcup_knowledge'
            ? 'RAG'
            : name === 'read_skill_file'
              ? 'SKILL'
              : 'MCP'
        patch({ tool: `${name} · ${proto}`, pending: true })
      }
    },
    onError: (detail) => {
      patch({ text: answer || `⚠️ ${detail}`, pending: false })
    },
    onDone: () => {
      // The coach caps answers around 150 words to keep token cost down. When an
      // answer runs long, surface a small italic note so the cap is transparent.
      const wordCount = answer.trim().split(/\s+/).filter(Boolean).length
      patch({
        pending: false,
        footnote:
          wordCount >= 140
            ? 'Response kept brief (~150 words) for cost optimization.'
            : undefined,
      })
    },
  })

  busy.value = false
  await scrollToBottom()
}
</script>

<template>
  <div class="chat">
    <div ref="scroller" class="messages">
      <MessageBubble
        v-for="m in messages"
        :key="m.id"
        :role="m.role"
        :text="m.text"
        :source="m.source"
        :tool="m.tool"
        :pending="m.pending"
        :note="m.note"
        :footnote="m.footnote"
      />
    </div>

    <div class="samples">
      <button
        v-for="q in SAMPLE_QUESTIONS"
        :key="q"
        class="chip"
        :disabled="busy"
        @click="send(q)"
      >
        {{ q }}
      </button>
    </div>

    <form class="composer" @submit.prevent="send()">
      <input
        v-model="input"
        :disabled="busy"
        placeholder="Hey! How can I help you today?"
        autocomplete="off"
      />
      <button type="submit" :disabled="busy || !input.trim()">Send</button>
    </form>
  </div>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  min-height: 0;
}
.samples {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}
.chip {
  width: 100%;
  text-align: left;
  background: rgba(255, 255, 255, 0.04);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 12px;
  padding: 0.45rem 0.8rem;
  font-size: 0.74rem;
  cursor: pointer;
  transition: background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}
.chip:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(148, 163, 184, 0.35);
  transform: translateY(-1px);
}
.chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.composer {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
}
.composer input {
  flex: 1;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  border-radius: 12px;
  padding: 0.72rem 0.95rem;
  font-size: 0.95rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}
.composer input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}
.composer button {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  border: none;
  border-radius: 12px;
  padding: 0 1.3rem;
  font-weight: 600;
  cursor: pointer;
  transition: filter 0.18s ease, transform 0.18s ease;
}
.composer button:hover:not(:disabled) {
  filter: brightness(1.08);
  transform: translateY(-1px);
}
.composer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
