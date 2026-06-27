<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { type Fixture } from '../api/footballMock'
import { fetchSchedule } from '../api/football'

const fixtures = ref<Fixture[]>([])
const source = ref<'live' | 'sample'>('sample')

// Local timezone label (e.g. "PDT", "GMT+5:30") shown next to kickoff times.
const tzLabel = new Intl.DateTimeFormat('en-US', { timeZoneName: 'short' })
  .formatToParts(new Date())
  .find((p) => p.type === 'timeZoneName')?.value ?? 'local'

// Local calendar date (YYYY-MM-DD) used for grouping, derived from the UTC
// kickoff when available so matches land on the viewer's local day.
function localDateKey(f: Fixture): string {
  if (!f.kickoff) return f.date
  return dateKeyOf(new Date(f.kickoff))
}

// Kickoff time in the browser's local timezone (falls back to the UTC field).
function localTime(f: Fixture): string {
  if (!f.kickoff) return `${f.time} UTC`
  const t = new Date(f.kickoff).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
  return `${t} ${tzLabel}`
}

// Local "today" key — fixtures before this local day are hidden so the view
// starts from today onwards (what's happening now / next).
function dateKeyOf(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
const todayKey = dateKeyOf(new Date())

const grouped = computed(() => {
  const map = new Map<string, Fixture[]>()
  for (const f of fixtures.value) {
    const key = localDateKey(f)
    if (key < todayKey) continue // skip past (local) days
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(f)
  }
  // Sort days, and matches within each day by local kickoff time.
  for (const list of map.values()) {
    list.sort((a, b) => (a.kickoff ?? a.time).localeCompare(b.kickoff ?? b.time))
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

onMounted(async () => {
  const res = await fetchSchedule()
  fixtures.value = res.fixtures
  source.value = res.source
})
</script>

<template>
  <div class="schedule">
    <div class="src-row">
      <span class="src" :class="source">{{ source === 'live' ? '● live' : 'sample data' }}</span>
    </div>
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
          <span v-else class="kickoff">{{ localTime(m) }}</span>
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
.src-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.6rem;
}
.src {
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 0.1rem 0.45rem;
  border-radius: 999px;
}
.src.live {
  background: #14532d;
  color: #86efac;
}
.src.sample {
  background: #422006;
  color: #fdba74;
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
