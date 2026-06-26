<script setup lang="ts">
import { ref } from 'vue'
import ChatPanel from './components/ChatPanel.vue'
import StandingsView from './components/StandingsView.vue'
import ScheduleView from './components/ScheduleView.vue'
import IntroSplash from './components/IntroSplash.vue'

type Tab = 'chat' | 'standings' | 'schedule'

const tab = ref<Tab>('chat')
const showIntro = ref(true)

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: 'chat', label: 'Ask AI', icon: '💬' },
  { id: 'standings', label: 'Standings', icon: '📊' },
  { id: 'schedule', label: 'Schedule', icon: '🗓️' },
]
</script>

<template>
  <IntroSplash v-if="showIntro" @done="showIntro = false" />

  <div class="app">
    <div class="glow glow-a"></div>
    <div class="glow glow-b"></div>
    <div class="glow glow-c"></div>
    <div class="pitch-lines" aria-hidden="true"></div>

    <header class="header">
      <div class="brand">
        <span class="logo" aria-hidden="true">
          <svg viewBox="0 0 48 48" width="40" height="40">
            <defs>
              <radialGradient id="ggBall" cx="38%" cy="32%" r="75%">
                <stop offset="0%" stop-color="#fff7d6" />
                <stop offset="45%" stop-color="#fcd34d" />
                <stop offset="100%" stop-color="#b45309" />
              </radialGradient>
            </defs>
            <circle cx="24" cy="24" r="21" fill="url(#ggBall)" stroke="#78350f" stroke-width="1.5" />
            <path
              d="M24 13l6 4.4-2.3 7.1h-7.4L18 17.4 24 13z"
              fill="#1e293b"
            />
            <path
              d="M24 13l6 4.4M24 13l-6 4.4M30 17.4l5.6-1.4M18 17.4l-5.6-1.4M27.7 24.5l4 5.6M20.3 24.5l-4 5.6M24 32l3 4M24 32l-3 4"
              stroke="#1e293b"
              stroke-width="1.4"
              fill="none"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <div class="brand-text">
          <h1>Golden<span class="gold">Goal</span></h1>
          <p>World Cup 2026 · RAG + MCP + Agent</p>
        </div>
      </div>
      <span class="phase">Phase 1 · mock data</span>
    </header>

    <section class="hero" aria-label="World Cup 2026">
      <div class="hero-stripes" aria-hidden="true"></div>
      <div class="hero-content">
        <span class="hero-kicker">⚽ Kickoff · June 2026</span>
        <h2 class="hero-title">The road to the <span class="gold">Golden Goal</span></h2>
        <p class="hero-sub">Live scores, standings &amp; AI-powered insights across USA · Canada · Mexico</p>
      </div>
      <div class="hero-flags" aria-hidden="true">
        <span class="flag">🇺🇸</span>
        <span class="flag">🇨🇦</span>
        <span class="flag">🇲🇽</span>
      </div>
      <span class="hero-ball hero-ball-1" aria-hidden="true">⚽</span>
      <span class="hero-ball hero-ball-2" aria-hidden="true">🏆</span>
    </section>

    <nav class="tabs">
      <button
        v-for="t in tabs"
        :key="t.id"
        class="tab"
        :class="{ active: tab === t.id }"
        @click="tab = t.id"
      >
        <span class="tab-icon">{{ t.icon }}</span>{{ t.label }}
      </button>
    </nav>

    <main class="main">
      <KeepAlive>
        <ChatPanel v-if="tab === 'chat'" />
        <StandingsView v-else-if="tab === 'standings'" />
        <ScheduleView v-else />
      </KeepAlive>
    </main>
  </div>
</template>

<style scoped>
.app {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 880px;
  margin: 0 auto;
  overflow: hidden;
}
.glow {
  position: absolute;
  width: 420px;
  height: 420px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.5;
  pointer-events: none;
  z-index: -1;
}
.glow-a {
  background: #2563eb;
  top: -160px;
  left: -120px;
}
.glow-b {
  background: #7c3aed;
  bottom: -180px;
  right: -120px;
}
.glow-c {
  background: #f59e0b;
  top: 38%;
  left: 50%;
  width: 320px;
  height: 320px;
  transform: translateX(-50%);
  opacity: 0.22;
}
.pitch-lines {
  position: absolute;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: 0.5;
  background:
    repeating-linear-gradient(
      90deg,
      rgba(148, 163, 184, 0.04) 0 38px,
      rgba(148, 163, 184, 0) 38px 76px
    );
  -webkit-mask-image: radial-gradient(120% 80% at 50% 30%, #000 30%, transparent 75%);
  mask-image: radial-gradient(120% 80% at 50% 30%, #000 30%, transparent 75%);
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.2rem 0.8rem;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}
.logo {
  display: inline-flex;
  filter: drop-shadow(0 4px 12px rgba(245, 158, 11, 0.45));
}
.brand-text h1 {
  margin: 0;
  font-family: var(--font-brand);
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #f8fafc;
}
.brand-text h1 .gold {
  background: linear-gradient(135deg, #fde68a, #f59e0b, #b45309);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.brand-text p {
  margin: 0;
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: #94a3b8;
}
.phase {
  font-family: var(--font-display);
  font-size: 0.64rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  color: #fbbf24;
  border: 1px solid rgba(120, 53, 15, 0.8);
  background: rgba(69, 26, 3, 0.6);
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}

/* ---- Hero banner ---- */
.hero {
  position: relative;
  margin: 0.4rem 1.2rem 0.2rem;
  padding: 1.1rem 1.3rem;
  border-radius: 18px;
  overflow: hidden;
  background:
    linear-gradient(120deg, rgba(15, 23, 42, 0.2), rgba(15, 23, 42, 0.55)),
    radial-gradient(140% 120% at 0% 0%, #1f8a3b 0%, #157a32 38%, #0c5a23 100%);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 14px 30px rgba(12, 90, 35, 0.28);
}
.hero-stripes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0 10%,
    rgba(0, 0, 0, 0.05) 10% 20%
  );
}
.hero-content {
  position: relative;
  z-index: 1;
}
.hero-kicker {
  display: inline-block;
  font-family: var(--font-display);
  font-size: 0.66rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #ecfccb;
  background: rgba(12, 90, 35, 0.55);
  border: 1px solid rgba(236, 252, 203, 0.3);
  padding: 0.22rem 0.6rem;
  border-radius: 999px;
}
.hero-title {
  margin: 0.55rem 0 0.25rem;
  font-family: var(--font-brand);
  font-size: clamp(1.3rem, 3.6vw, 1.9rem);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: #f8fafc;
  text-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
}
.hero-title .gold {
  background: linear-gradient(135deg, #fde68a, #f59e0b, #b45309);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-sub {
  margin: 0;
  max-width: 30rem;
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 500;
  color: #d1fae5;
}
.hero-flags {
  position: absolute;
  top: 0.9rem;
  right: 1.1rem;
  z-index: 1;
  display: flex;
  gap: 0.3rem;
  font-size: 1.15rem;
  filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.45));
}
.hero-ball {
  position: absolute;
  pointer-events: none;
  opacity: 0.9;
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.45));
}
.hero-ball-1 {
  right: 1.4rem;
  bottom: -0.6rem;
  font-size: 3.2rem;
  animation: floatBall 4s ease-in-out infinite;
}
.hero-ball-2 {
  right: 5.2rem;
  top: 2.4rem;
  font-size: 1.5rem;
  opacity: 0.85;
  animation: floatBall 5s ease-in-out infinite 0.6s;
}
@keyframes floatBall {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-8px) rotate(12deg);
  }
}
@media (prefers-reduced-motion: reduce) {
  .hero-ball {
    animation: none;
  }
}
.tabs {
  display: flex;
  gap: 0.35rem;
  padding: 0.4rem;
  margin: 0.4rem 1.2rem 0.6rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 14px;
}
.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.55rem 0.6rem;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #94a3b8;
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: all 0.15s ease;
}
.tab:hover {
  color: #e2e8f0;
}
.tab.active {
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
}
.tab-icon {
  font-size: 1rem;
}
.main {
  flex: 1;
  min-height: 0;
  margin: 0 0.6rem 0.6rem;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 18px;
  overflow: hidden;
  backdrop-filter: blur(12px);
}
</style>
