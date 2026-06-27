<script setup lang="ts">
import type { AnswerSource } from '../api/types'

const props = defineProps<{
  role: 'user' | 'assistant'
  text: string
  source?: AnswerSource
  tool?: string
  pending?: boolean
  note?: boolean
}>()

const BADGE: Record<AnswerSource, { label: string; cls: string }> = {
  live: { label: 'LIVE', cls: 'badge-live' },
  rag: { label: 'RAG', cls: 'badge-rag' },
  agent: { label: 'COACH', cls: 'badge-agent' },
  mcp: { label: 'MCP', cls: 'badge-mcp' },
}
</script>

<template>
  <div v-if="props.note" class="note-row">
    <span class="note">{{ props.text }}</span>
  </div>
  <div v-else class="row" :class="props.role">
    <div class="bubble" :class="props.role">
      <div v-if="props.role === 'assistant' && props.source" class="meta">
        <span class="badge" :class="BADGE[props.source].cls">{{ BADGE[props.source].label }}</span>
        <span v-if="props.tool" class="tool">{{ props.tool }}</span>
      </div>
      <p v-if="props.pending" class="dots"><span>·</span><span>·</span><span>·</span></p>
      <p v-else class="text">{{ props.text }}</p>
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  margin: 0.5rem 0;
}
.note-row {
  display: flex;
  justify-content: center;
  margin: 0.5rem 0 0.1rem;
}
.note {
  font-size: 0.72rem;
  color: #94a3b8;
  background: #0f172a;
  border: 1px dashed #334155;
  border-radius: 999px;
  padding: 0.25rem 0.7rem;
  text-align: center;
  max-width: 90%;
}
.row.user {
  justify-content: flex-end;
}
.bubble {
  max-width: 78%;
  padding: 0.75rem 0.95rem;
  border-radius: 16px;
  line-height: 1.5;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.22);
}
.bubble.user {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: #fff;
  border-bottom-right-radius: 5px;
}
.bubble.assistant {
  background: rgba(30, 41, 59, 0.85);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-bottom-left-radius: 5px;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}
.meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.badge {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
}
.badge-live {
  background: #7f1d1d;
  color: #fecaca;
}
.badge-rag {
  background: #1e3a8a;
  color: #bfdbfe;
}
.badge-agent {
  background: #4c1d95;
  color: #ddd6fe;
}
.badge-mcp {
  background: #78350f;
  color: #fed7aa;
}
.tool {
  font-size: 0.68rem;
  color: #94a3b8;
}
.text {
  margin: 0;
  white-space: pre-wrap;
}
.dots span {
  animation: blink 1.2s infinite;
  font-size: 1.3rem;
}
.dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.dots span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes blink {
  0%, 60%, 100% {
    opacity: 0.25;
  }
  30% {
    opacity: 1;
  }
}
</style>
