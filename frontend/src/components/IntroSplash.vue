<script setup lang="ts">
import { onMounted, ref } from 'vue'

const emit = defineEmits<{ done: [] }>()
const hiding = ref(false)

onMounted(() => {
  // Start fade-out near the end of the ball animation, then unmount.
  window.setTimeout(() => (hiding.value = true), 2600)
  window.setTimeout(() => emit('done'), 3200)
})
</script>

<template>
  <div class="splash" :class="{ hide: hiding }">
    <!-- Soccer field -->
    <div class="pitch">
      <div class="stripes"></div>
      <div class="halfway"></div>
      <div class="center-circle"></div>
      <div class="center-spot"></div>
    </div>

    <!-- Big goal posts on each side -->
    <div class="goal goal-left">
      <span class="post post-top"></span>
      <span class="post post-bottom"></span>
      <span class="post post-back"></span>
    </div>
    <div class="goal goal-right">
      <span class="post post-top"></span>
      <span class="post post-bottom"></span>
      <span class="post post-back"></span>
    </div>

    <!-- Footballs kicked in from both sides -->
    <span class="ball ball-left">⚽</span>
    <span class="ball ball-right">⚽</span>

    <!-- Impact flash + title -->
    <div class="flash"></div>
    <div class="title">
      <span class="word">Golden</span><span class="word gold">Goal</span>
      <div class="tag">World Cup 2026 AI</div>
    </div>
  </div>
</template>

<style scoped>
.splash {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  transition: opacity 0.55s ease, visibility 0.55s ease;
}
.splash.hide {
  opacity: 0;
  visibility: hidden;
}

/* ---- Soccer field ---- */
.pitch {
  position: absolute;
  inset: 0;
  background: radial-gradient(120% 90% at 50% 50%, #1f8a3b 0%, #157a32 45%, #0c5a23 100%);
}
.stripes {
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.05) 0 8%,
    rgba(0, 0, 0, 0.05) 8% 16%
  );
  opacity: 0.6;
}
.halfway {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 4px;
  transform: translateX(-50%);
  background: rgba(255, 255, 255, 0.55);
}
.center-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  width: clamp(180px, 26vw, 320px);
  height: clamp(180px, 26vw, 320px);
  transform: translate(-50%, -50%);
  border: 4px solid rgba(255, 255, 255, 0.55);
  border-radius: 50%;
}
.center-spot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 12px;
  height: 12px;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
}

/* ---- Big goal posts ---- */
.goal {
  position: absolute;
  top: 50%;
  width: clamp(70px, 9vw, 120px);
  height: clamp(260px, 46vh, 460px);
  transform: translateY(-50%);
  opacity: 0;
  animation: goalIn 0.6s ease forwards;
}
.goal-left {
  left: 0;
}
.goal-right {
  right: 0;
  transform: translateY(-50%) scaleX(-1);
}
/* netting */
.goal::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.22) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.22) 1px, transparent 1px);
  background-size: 13px 13px;
  -webkit-mask-image: linear-gradient(90deg, #000 0%, rgba(0, 0, 0, 0.15) 100%);
  mask-image: linear-gradient(90deg, #000 0%, rgba(0, 0, 0, 0.15) 100%);
}
.post {
  position: absolute;
  background: #f8fafc;
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.5);
  border-radius: 3px;
}
.post-top {
  top: 0;
  left: 0;
  right: 0;
  height: 8px;
}
.post-bottom {
  bottom: 0;
  left: 0;
  right: 0;
  height: 8px;
}
.post-back {
  top: 0;
  bottom: 0;
  right: 0;
  width: 8px;
}

/* ---- Balls ---- */
.ball {
  position: absolute;
  top: 50%;
  font-size: clamp(3rem, 6vw, 4.2rem);
  filter: drop-shadow(0 10px 18px rgba(0, 0, 0, 0.55));
}
.ball-left {
  left: clamp(70px, 9vw, 120px);
  animation: kickRight 1.5s cubic-bezier(0.2, 0.7, 0.3, 1) forwards;
}
.ball-right {
  right: clamp(70px, 9vw, 120px);
  animation: kickLeft 1.5s cubic-bezier(0.2, 0.7, 0.3, 1) 0.25s forwards;
}

/* Impact flash where they meet */
.flash {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #fde68a;
  opacity: 0;
  animation: flash 0.5s ease 1.7s forwards;
}

/* Title reveal */
.title {
  position: relative;
  text-align: center;
  opacity: 0;
  transform: scale(0.6);
  animation: titleIn 0.7s cubic-bezier(0.2, 1.4, 0.4, 1) 1.85s forwards;
  text-shadow: 0 6px 26px rgba(0, 0, 0, 0.45);
}
.word {
  font-family: var(--font-brand);
  font-size: clamp(2.6rem, 9vw, 4.8rem);
  font-weight: 800;
  letter-spacing: -0.04em;
  background: linear-gradient(135deg, #ffffff, #cbd5e1);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
.word.gold {
  background: linear-gradient(135deg, #fde68a, #f59e0b, #b45309);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 4px 14px rgba(245, 158, 11, 0.45));
}
.tag {
  margin-top: 0.5rem;
  font-family: var(--font-display);
  font-size: 0.78rem;
  font-weight: 500;
  letter-spacing: 0.38em;
  text-transform: uppercase;
  color: #e2e8f0;
}

@keyframes kickRight {
  0% {
    transform: translate(0, -50%) rotate(0deg);
  }
  100% {
    transform: translate(calc(50vw - clamp(120px, 13vw, 170px)), -50%) rotate(1080deg);
  }
}
@keyframes kickLeft {
  0% {
    transform: translate(0, -50%) rotate(0deg);
  }
  100% {
    transform: translate(calc(-50vw + clamp(120px, 13vw, 170px)), -50%) rotate(-1080deg);
  }
}
@keyframes flash {
  0% {
    opacity: 0;
    transform: scale(0.3);
    box-shadow: 0 0 0 0 rgba(253, 230, 138, 0.7);
  }
  40% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 50px 22px rgba(253, 230, 138, 0.55);
  }
  100% {
    opacity: 0;
    transform: scale(2.6);
    box-shadow: 0 0 70px 34px rgba(253, 230, 138, 0);
  }
}
@keyframes titleIn {
  to {
    opacity: 1;
    transform: scale(1);
  }
}
@keyframes goalIn {
  to {
    opacity: 1;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ball,
  .flash {
    display: none;
  }
  .title {
    animation: titleIn 0.4s ease forwards;
  }
}
</style>
