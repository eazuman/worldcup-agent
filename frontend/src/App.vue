<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ChatPanel from './components/ChatPanel.vue'
import StandingsView from './components/StandingsView.vue'
import ScheduleView from './components/ScheduleView.vue'
import PredictView from './components/PredictView.vue'
import IntroSplash from './components/IntroSplash.vue'
import { fetchDataMode } from './api/football'

type Tab = 'chat' | 'standings' | 'schedule' | 'predict'

const tab = ref<Tab>('chat')
const showIntro = ref(true)
const dataMode = ref<'live' | 'sample'>('sample')

const tabs: { id: Tab; label: string; icon: string }[] = [
  { id: 'chat', label: 'Ask AI', icon: '💬' },
  { id: 'schedule', label: 'Schedule & Scores', icon: '🗓️' },
  { id: 'standings', label: 'Standings', icon: '📊' },
  { id: 'predict', label: 'Predict', icon: '🔮' },
]

onMounted(async () => {
  try {
    dataMode.value = await fetchDataMode()
  } catch {
    dataMode.value = 'sample'
  }
})
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
          <svg viewBox="0 0 64 64" width="46" height="46" role="img" aria-label="GoldenGoal logo">
            <defs>
              <linearGradient id="ggGold" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#fde68a" />
                <stop offset="50%" stop-color="#f59e0b" />
                <stop offset="100%" stop-color="#b45309" />
              </linearGradient>
              <linearGradient id="ggDark" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#1e293b" />
                <stop offset="100%" stop-color="#0b1220" />
              </linearGradient>
              <radialGradient id="ggBall" cx="38%" cy="30%" r="75%">
                <stop offset="0%" stop-color="#ffffff" />
                <stop offset="60%" stop-color="#e2e8f0" />
                <stop offset="100%" stop-color="#94a3b8" />
              </radialGradient>
            </defs>
            <!-- modern hexagon badge -->
            <path
              d="M32 3 L55 16.5 V43.5 L32 57 L9 43.5 V16.5 Z"
              fill="url(#ggDark)"
              stroke="url(#ggGold)"
              stroke-width="2.5"
              stroke-linejoin="round"
            />
            <!-- dynamic golden motion swoosh -->
            <path
              d="M13 41 Q31 51 51 28"
              fill="none"
              stroke="url(#ggGold)"
              stroke-width="3"
              stroke-linecap="round"
              opacity="0.9"
            />
            <!-- stylized soccer ball -->
            <g class="logo-ball">
              <circle cx="32" cy="29" r="12.5" fill="url(#ggBall)" />
              <polygon points="32,24 36.76,27.45 34.94,33.05 29.06,33.05 27.25,27.45" fill="#1f2937" />
              <g stroke="#1f2937" stroke-width="1.6" fill="none" stroke-linecap="round">
                <line x1="32" y1="24" x2="32" y2="16.5" />
                <line x1="36.76" y1="27.45" x2="43.89" y2="25.14" />
                <line x1="34.94" y1="33.05" x2="39.35" y2="39.11" />
                <line x1="29.06" y1="33.05" x2="24.65" y2="39.11" />
                <line x1="27.25" y1="27.45" x2="20.11" y2="25.14" />
              </g>
            </g>
          </svg>
        </span>
        <div class="brand-text">
          <h1>G<span class="o-ball" aria-hidden="true">⚽</span>lden<span class="gold">G<span class="o-ball" aria-hidden="true">⚽</span>al</span></h1>
          <p>World Cup 2026 · RAG + MCP + SKILLS + Agent</p>
        </div>
      </div>
      <span class="phase" :class="dataMode === 'live' ? 'phase-live' : 'phase-mock'">
        {{ dataMode === 'live' ? '● live data' : '● mock data' }}
      </span>
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
      <div class="hero-scene" aria-hidden="true">
        <span class="hero-trophy">🏆</span>
        <span class="hero-ball">⚽</span>
        <span class="hero-ball-shadow"></span>
      </div>
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
        <PredictView v-else-if="tab === 'predict'" />
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
  filter: drop-shadow(0 4px 14px rgba(245, 158, 11, 0.5));
}
.logo-ball {
  transform-box: fill-box;
  transform-origin: center;
  animation: brandBallSpin 14s linear infinite;
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
.brand-text h1 .o-ball {
  display: inline-block;
  font-size: 0.86em;
  line-height: 1;
  vertical-align: -0.04em;
  margin: 0 0.01em;
  -webkit-text-fill-color: initial;
  animation: brandBallSpin 9s linear infinite;
}
@keyframes brandBallSpin {
  to {
    transform: rotate(360deg);
  }
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
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  white-space: nowrap;
}
.phase-mock {
  color: #fbbf24;
  border: 1px solid rgba(120, 53, 15, 0.8);
  background: rgba(69, 26, 3, 0.6);
}
.phase-live {
  color: #86efac;
  border: 1px solid rgba(21, 128, 61, 0.8);
  background: rgba(20, 83, 45, 0.55);
}

/* ---- Hero banner ---- */
.hero {
  position: relative;
  margin: 0.4rem 1.2rem 0.2rem;
  padding: 1.2rem 1.4rem;
  border-radius: 20px;
  overflow: hidden;
  background:
    radial-gradient(120% 140% at 85% -20%, rgba(52, 211, 153, 0.28), transparent 55%),
    radial-gradient(100% 120% at 0% 120%, rgba(5, 46, 22, 0.6), transparent 60%),
    linear-gradient(135deg, #0d3d22 0%, #0a5a30 45%, #073d20 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    inset 0 0 60px rgba(0, 0, 0, 0.25),
    0 18px 40px rgba(4, 47, 22, 0.45);
}
.hero-stripes {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.022) 0 9%,
    rgba(0, 0, 0, 0.03) 9% 18%
  );
  -webkit-mask-image: linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent);
  mask-image: linear-gradient(90deg, transparent, #000 30%, #000 70%, transparent);
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
/* ---- Hero scene: trophy + bouncing ball ---- */
.hero-scene {
  position: absolute;
  right: 1.2rem;
  bottom: 0.4rem;
  z-index: 1;
  width: 7.5rem;
  height: 4.2rem;
  pointer-events: none;
}
.hero-trophy {
  position: absolute;
  left: 0.2rem;
  bottom: 0.3rem;
  font-size: 2.2rem;
  filter: drop-shadow(0 4px 10px rgba(180, 83, 9, 0.5));
  animation: trophyBob 3.4s ease-in-out infinite;
}
.hero-ball {
  position: absolute;
  right: 0.7rem;
  bottom: 0.5rem;
  font-size: 3rem;
  transform-origin: 50% 100%;
  filter: drop-shadow(0 5px 8px rgba(0, 0, 0, 0.35));
  animation: ballBounce 1.8s ease-in-out infinite;
}
.hero-ball-shadow {
  position: absolute;
  right: 1rem;
  bottom: 0.35rem;
  width: 2.3rem;
  height: 0.55rem;
  border-radius: 50%;
  background: radial-gradient(closest-side, rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0));
  animation: ballShadow 1.8s ease-in-out infinite;
}
@keyframes ballBounce {
  0%, 100% {
    transform: translateY(0) scale(1.04, 0.96); /* gentle squash on contact */
  }
  18% {
    transform: translateY(0) scale(1, 1);
  }
  50% {
    transform: translateY(-12px) scale(1, 1); /* slight lift, no spin */
  }
}
@keyframes ballShadow {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(0.7);
    opacity: 0.28;
  }
}
@keyframes trophyBob {
  0%, 100% {
    transform: translateY(0) rotate(-3deg);
  }
  50% {
    transform: translateY(-5px) rotate(3deg);
  }
}
@media (prefers-reduced-motion: reduce) {
  .hero-ball,
  .hero-ball-shadow,
  .hero-trophy {
    animation: none;
  }
  .hero-ball {
    transform: translateY(0);
  }
}
.tabs {
  display: flex;
  gap: 0.35rem;
  padding: 0.35rem;
  margin: 0.4rem 1.2rem 0.6rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 0.6rem;
  border: 1px solid transparent;
  border-radius: 11px;
  background: transparent;
  color: #94a3b8;
  font-family: var(--font-display);
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: color 0.18s ease, background 0.18s ease, transform 0.18s ease,
    box-shadow 0.18s ease;
}
.tab:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}
.tab.active {
  color: #fff;
  background: linear-gradient(135deg, #3b82f6, #7c3aed);
  border-color: rgba(255, 255, 255, 0.14);
  box-shadow:
    0 8px 22px rgba(37, 99, 235, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}
.tab.active:hover {
  background: linear-gradient(135deg, #3b82f6, #7c3aed);
}
.tab-icon {
  font-size: 1rem;
}
.main {
  flex: 1;
  min-height: 0;
  margin: 0 0.6rem 0.6rem;
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.045),
    rgba(15, 23, 42, 0.55)
  );
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 20px;
  overflow: hidden;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    0 20px 50px rgba(0, 0, 0, 0.35);
}
</style>
