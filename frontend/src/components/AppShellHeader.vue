<template>
  <!--
    AppShellHeader — shared SPA application header band.

    Replaces the per-page <header class="app-shell-header"> blocks that were
    previously duplicated across each Jinja template. Uses the existing
    app-shell-* CSS classes from static/css/common.css (loaded by spa.html).

    Title and subtitle are driven by route meta so each page can declare its
    own heading without per-page shell duplication. Navigation uses RouterLink
    so transitions are fully client-side inside the SPA.
  -->
  <header class="app-shell-header">
    <div class="app-shell-title">{{ title }}</div>
    <div v-if="subtitle" class="app-shell-subtitle">{{ subtitle }}</div>

    <nav class="app-shell-nav" aria-label="Основна навігація">
      <RouterLink
        v-for="link in NAV_LINKS"
        :key="link.to"
        :to="link.to"
        class="app-shell-nav-link"
        active-class=""
        exact-active-class="active"
        :aria-current="isExact(link.to) ? 'page' : undefined"
      >
        {{ link.label }}
      </RouterLink>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const title = computed<string>(
  () => (route.meta.title as string | undefined) ?? 'Pricewatch',
)
const subtitle = computed<string | undefined>(
  () => route.meta.subtitle as string | undefined,
)

// Navigation links — all four operator-facing routes.
// exact-active-class="active" (active-class="" disables prefix-match highlight)
// ensures only the exactly-matched link is highlighted; without this the "/"
// link would appear active on every page due to Vue Router's prefix matching.
const NAV_LINKS = [
  { to: '/',        label: '🏠 Порівняння' },
  { to: '/service', label: '🔧 Service Console' },
  { to: '/gap',     label: '📋 Розрив асортименту' },
  { to: '/matches', label: '✅ Підтверджені збіги' },
] as const

/** True when the current path exactly matches the given link target. */
function isExact(to: string): boolean {
  return route.path === to
}
</script>

