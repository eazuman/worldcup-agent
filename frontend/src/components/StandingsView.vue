<script setup lang="ts">
import { computed } from 'vue'
import { GROUPS, type TeamRow } from '../api/footballMock'

function sortTable(table: TeamRow[]): TeamRow[] {
  return [...table].sort(
    (a, b) => b.points - a.points || b.gf - b.ga - (a.gf - a.ga) || b.gf - a.gf,
  )
}

const groups = computed(() =>
  GROUPS.map((g) => ({ name: g.name, table: sortTable(g.table) })),
)
</script>

<template>
  <div class="standings">
    <div class="hint">
      <span class="dot qualify"></span> Top 2 advance
      <span class="dot third"></span> Best 8 third-placed teams also advance · 48 teams · 12 groups
    </div>

    <div class="grid">
      <section v-for="g in groups" :key="g.name" class="card">
        <header class="card-head">Group {{ g.name }}</header>
        <table>
          <thead>
            <tr>
              <th class="left">#</th>
              <th class="left team-col">Team</th>
              <th>P</th>
              <th>W</th>
              <th>D</th>
              <th>L</th>
              <th>GD</th>
              <th>Pts</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(t, i) in g.table"
              :key="t.team"
              :class="{ qualify: i < 2, third: i === 2 }"
            >
              <td class="left rank">{{ i + 1 }}</td>
              <td class="left team">
                <span class="flag">{{ t.flag }}</span>{{ t.team }}
              </td>
              <td>{{ t.played }}</td>
              <td>{{ t.won }}</td>
              <td>{{ t.drawn }}</td>
              <td>{{ t.lost }}</td>
              <td>{{ t.gf - t.ga > 0 ? '+' : '' }}{{ t.gf - t.ga }}</td>
              <td class="pts">{{ t.points }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<style scoped>
.standings {
  height: 100%;
  overflow-y: auto;
  padding: 1rem 1.1rem 2rem;
}
.hint {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
  font-size: 0.72rem;
  color: #94a3b8;
  margin-bottom: 1rem;
}
.dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
  margin-left: 0.6rem;
}
.dot.qualify {
  background: #22c55e;
}
.dot.third {
  background: #eab308;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 0.9rem;
}
.card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 16px;
  overflow: hidden;
  backdrop-filter: blur(8px);
}
.card-head {
  padding: 0.6rem 0.9rem;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 0.82rem;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.25), rgba(124, 58, 237, 0.2));
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}
th {
  font-weight: 600;
  color: #64748b;
  padding: 0.45rem 0.3rem;
  text-align: center;
}
td {
  padding: 0.5rem 0.3rem;
  text-align: center;
  border-top: 1px solid rgba(148, 163, 184, 0.07);
}
.left {
  text-align: left;
  padding-left: 0.7rem;
}
.team-col {
  width: 45%;
}
.team {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  white-space: nowrap;
}
.flag {
  font-size: 1rem;
}
.rank {
  color: #64748b;
}
.pts {
  font-family: var(--font-display);
  font-weight: 700;
  color: #e2e8f0;
}
tr.qualify {
  box-shadow: inset 3px 0 0 #22c55e;
}
tr.third {
  box-shadow: inset 3px 0 0 #eab308;
}
</style>
