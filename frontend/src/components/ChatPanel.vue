<script setup lang="ts">
import { nextTick, ref } from 'vue'
import MessageBubble from './MessageBubble.vue'
import { askMock, SAMPLE_QUESTIONS } from '../api/mock'
import type { ChatMessage } from '../api/types'

const messages = ref<ChatMessage[]>([
  {
    id: 0,
    role: 'assistant',
    text:
      "Hi! Ask me anything about the FIFA World Cup 2026 — fixtures, standings, " +
      "team history, or live scores. (Phase 1: answers are mock data.)",
    source: 'agent',
    tool: 'agent · RAG + live',
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
  const pendingId = nextId++
  messages.value.push({ id: pendingId, role: 'assistant', text: '', pending: true })
  await scrollToBottom()

  const res = await askMock(question)
  const idx = messages.value.findIndex((m) => m.id === pendingId)
  if (idx !== -1) {
    messages.value[idx] = {
      id: pendingId,
      role: 'assistant',
      text: res.answer,
      source: res.source,
      tool: res.tool,
    }
  }
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
        placeholder="Ask about World Cup 2026…"
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
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-top: 1px solid #1e293b;
}
.chip {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #334155;
  border-radius: 999px;
  padding: 0.3rem 0.7rem;
  font-size: 0.74rem;
  cursor: pointer;
}
.chip:hover:not(:disabled) {
  background: #1e293b;
}
.chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.composer {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem 1rem;
  border-top: 1px solid #1e293b;
}
.composer input {
  flex: 1;
  background: #0f172a;
  border: 1px solid #334155;
  color: #e2e8f0;
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  font-size: 0.95rem;
}
.composer input:focus {
  outline: none;
  border-color: #2563eb;
}
.composer button {
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 10px;
  padding: 0 1.2rem;
  font-weight: 600;
  cursor: pointer;
}
.composer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
