<script setup lang="ts">
import { computed } from 'vue'
import { FIXTURES, type Fixture } from '../api/footballMock'

const grouped = computed(() => {
  const map = new Map<string, Fixture[]>()
  for (const f of FIXTURES) {
    if (!map.has(f.date)) map.set(f.date, [])
    map.get(f.date)!.push(f)
  }
  return [...map.entries()].sort(([a], [b]) => a.localeCompare(b))
})

function prettyDate(iso: string): string {
  return new Date(iso + 'T00:00:00').toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="schedule">
    <div v-for="[date, matches] in grouped" :key="date" class="day">
      <h3 class="day-head">{{ prettyDate(date) }}</h3>

      <div
        v-for="m in matches"
        :key="m.id"
        class="match"
        :class="{ live: m.status === 'LIVE' }"
      >
        <div class="meta">
          <span class="stage">{{ m.stage }}<template v-if="m.group"> · Group {{ m.group }}</template></span>
          <span v-if="m.status === 'LIVE'" class="live-badge">● LIVE</span>
          <span v-else class="kickoff">{{ m.time }} UTC</span>
        </div>

        <div class="teams">
          <div class="side home">
            <span class="name">{{ m.home.team }}</span>
            <span class="flag">{{ m.home.flag }}</span>
          </div>

          <div class="center">
            <template v-if="m.score">
              <span class="score">{{ m.score.home }}</span>
              <span class="sep">:</span>
              <span class="score">{{ m.score.away }}</span>
            </template>
            <span v-else class="vs">vs</span>
          </div>

          <div class="side away">
            <span class="flag">{{ m.away.flag }}</span>
            <span class="name">{{ m.away.team }}</span>
          </div>
        </div>

        <div class="venue">📍 {{ m.venue }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.schedule {
  height: 100%;
  overflow-y: auto;
  padding: 1rem 1.1rem 2rem;
}
.day {
  margin-bottom: 1.4rem;
}
.day-head {
  font-family: var(--font-display);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin: 0 0 0.6rem;
}
.match {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 16px;
  padding: 0.8rem 1rem;
  margin-bottom: 0.6rem;
  backdrop-filter: blur(8px);
  transition: transform 0.12s ease, border-color 0.12s ease;
}
.match:hover {
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.45);
}
.match.live {
  border-color: rgba(239, 68, 68, 0.5);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(255, 255, 255, 0.02));
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.68rem;
  color: #64748b;
  margin-bottom: 0.55rem;
}
.live-badge {
  color: #f87171;
  font-weight: 700;
  animation: pulse 1.4s infinite;
}
.kickoff {
  color: #94a3b8;
  font-weight: 600;
}
.teams {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 0.6rem;
}
.side {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.side.home {
  justify-content: flex-end;
}
.side.away {
  justify-content: flex-start;
}
.name {
  font-weight: 600;
  font-size: 0.92rem;
}
.flag {
  font-size: 1.4rem;
}
.center {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 64px;
  justify-content: center;
}
.score {
  font-family: var(--font-display);
  font-size: 1.35rem;
  font-weight: 700;
}
.sep {
  color: #64748b;
}
.vs {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 600;
}
.venue {
  text-align: center;
  font-size: 0.68rem;
  color: #64748b;
  margin-top: 0.55rem;
}
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}
</style>
