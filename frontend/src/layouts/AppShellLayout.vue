<template>
  <!--
    AppShellLayout — full SPA application shell (Commit 6).

    Owns:
      - shared header band with title, subtitle, and client-side navigation
      - <main> content area that hosts the active route component via RouterView

    Header chrome is rendered by AppShellHeader which reads route.meta for
    per-route title/subtitle and uses RouterLink for in-app navigation.

    static/css/common.css (loaded by spa.html) provides all app-shell-* styles.
  -->
  <div class="app-shell">
    <AppShellHeader />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppShellHeader from '@/components/AppShellHeader.vue'
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  padding: 28px 24px 64px;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

@media (max-width: 720px) {
  main {
    padding: 18px 16px 48px;
  }
}
</style>



