<script setup lang="ts">
import { ref } from 'vue'
import { playPrediction, type PlayResult } from '../api/predict'

const guess = ref('')
const busy = ref(false)
const result = ref<PlayResult | null>(null)
const error = ref('')

async function play() {
  const value = guess.value.trim()
  if (!value || busy.value) return
  busy.value = true
  error.value = ''
  try {
    result.value = await playPrediction(value)
  } catch {
    error.value = 'Could not reach the coach. Is the backend running?'
  } finally {
    busy.value = false
  }
}

function reset() {
  result.value = null
  guess.value = ''
  error.value = ''
}
</script>

<template>
  <div class="predict">
    <div class="intro">
      <h3>🔮 Beat the Coach</h3>
      <p>
        Who lifts the 2026 World Cup? Type your pick and I'll reveal mine — based on
        World Cup pedigree, current goals scored, and the in-form striker. Match me
        and you win!
      </p>
    </div>

    <form v-if="!result" class="ask" @submit.prevent="play">
      <input
        v-model="guess"
        :disabled="busy"
        placeholder="Your champion pick… e.g. Brazil, France, Argentina"
        autocomplete="off"
      />
      <button type="submit" :disabled="busy || !guess.trim()">
        {{ busy ? 'Thinking…' : 'Lock in' }}
      </button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="result" class="result">
      <div class="verdict" :class="result.win ? 'win' : 'lose'">
        <span class="verdict-icon">{{ result.win ? '🏆' : '🤝' }}</span>
        <p>{{ result.reasoning }}</p>
      </div>

      <div class="pick">
        <span class="pick-label">My pick</span>
        <span class="pick-team">{{ result.factors.flag }} {{ result.predicted }}</span>
        <span class="pick-score">score {{ result.factors.score }}</span>
      </div>

      <div class="board">
        <div class="board-head">
          <span>Coach's power rankings</span>
          <span class="src" :class="result.source">
            {{ result.source === 'live' ? '● live data' : '● sample data' }}
          </span>
        </div>
        <div
          v-for="(t, i) in result.leaderboard"
          :key="t.team"
          class="row"
          :class="{ top: i === 0, you: result.matched === t.team }"
        >
          <span class="rank">{{ i + 1 }}</span>
          <span class="team">{{ t.flag }} {{ t.team }}</span>
          <span class="facts">
            <span class="tag">🏅 {{ t.titles }}</span>
            <span class="tag">⚽ {{ t.goals }}</span>
            <span v-if="t.star" class="tag star">👟 {{ t.star }} ({{ t.star_goals }})</span>
          </span>
          <span class="score">{{ t.score }}</span>
        </div>
      </div>

      <button class="again" @click="reset">Play again</button>
    </div>
  </div>
</template>

<style scoped>
.predict {
  height: 100%;
  overflow-y: auto;
  padding: 1.2rem;
}
.intro h3 {
  margin: 0 0 0.3rem;
  font-family: var(--font-brand);
  font-size: 1.15rem;
  color: #f8fafc;
}
.intro p {
  margin: 0 0 1rem;
  font-size: 0.85rem;
  line-height: 1.5;
  color: #94a3b8;
  max-width: 34rem;
}
.ask {
  display: flex;
  gap: 0.5rem;
}
.ask input {
  flex: 1;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  border-radius: 12px;
  padding: 0.72rem 0.95rem;
  font-size: 0.95rem;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}
.ask input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}
.ask button {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #1f2937;
  border: none;
  border-radius: 12px;
  padding: 0 1.3rem;
  font-weight: 700;
  cursor: pointer;
  transition: filter 0.18s ease, transform 0.18s ease;
}
.ask button:hover:not(:disabled) {
  filter: brightness(1.06);
  transform: translateY(-1px);
}
.ask button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.error {
  margin-top: 0.8rem;
  color: #fca5a5;
  font-size: 0.85rem;
}
.result {
  margin-top: 0.4rem;
}
.verdict {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.9rem 1rem;
  border-radius: 14px;
  border: 1px solid transparent;
}
.verdict p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.45;
  color: #f1f5f9;
}
.verdict-icon {
  font-size: 1.8rem;
}
.verdict.win {
  background: linear-gradient(135deg, rgba(21, 128, 61, 0.35), rgba(20, 83, 45, 0.25));
  border-color: rgba(74, 222, 128, 0.35);
}
.verdict.lose {
  background: linear-gradient(135deg, rgba(120, 53, 15, 0.3), rgba(69, 26, 3, 0.25));
  border-color: rgba(251, 191, 36, 0.3);
}
.pick {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin: 1rem 0 0.5rem;
}
.pick-label {
  font-size: 0.7rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #94a3b8;
}
.pick-team {
  font-family: var(--font-brand);
  font-size: 1.1rem;
  font-weight: 700;
  color: #fde68a;
}
.pick-score {
  font-size: 0.74rem;
  color: #94a3b8;
}
.board {
  margin-top: 0.6rem;
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 14px;
  overflow: hidden;
}
.board-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.8rem;
  background: rgba(255, 255, 255, 0.04);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: #cbd5e1;
}
.src {
  font-weight: 600;
}
.src.live {
  color: #86efac;
}
.src.sample {
  color: #fbbf24;
}
.row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.8rem;
  border-top: 1px solid rgba(148, 163, 184, 0.08);
  font-size: 0.82rem;
}
.row.top {
  background: rgba(245, 158, 11, 0.08);
}
.row.you {
  box-shadow: inset 3px 0 0 #3b82f6;
}
.rank {
  width: 1.1rem;
  color: #94a3b8;
  font-weight: 700;
}
.team {
  flex: 1;
  font-weight: 600;
  color: #e2e8f0;
}
.facts {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}
.tag {
  font-size: 0.66rem;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 999px;
  padding: 0.1rem 0.45rem;
  white-space: nowrap;
}
.tag.star {
  color: #fde68a;
  border-color: rgba(245, 158, 11, 0.3);
}
.score {
  width: 2.5rem;
  text-align: right;
  font-weight: 700;
  color: #fde68a;
}
.again {
  margin-top: 1rem;
  background: rgba(255, 255, 255, 0.05);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  padding: 0.6rem 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s ease;
}
.again:hover {
  background: rgba(255, 255, 255, 0.1);
}

@media (max-width: 560px) {
  .facts {
    display: none;
  }
}
</style>
