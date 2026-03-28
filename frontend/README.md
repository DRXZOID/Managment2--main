# PriceWatch Frontend

Vue 3 + Vite + TypeScript frontend workspace for PriceWatch.

## Overview

This workspace provides the frontend build foundation for incremental Vue island adoption
over existing Flask-rendered pages. See `docs/adr/0014-incremental-vue-adoption.md`
for the architectural rationale.

## Development

Install dependencies:
```bash
npm install
```

Start Vite dev server (standalone — not yet wired into Flask):
```bash
npm run dev
```

Type-check:
```bash
npm run typecheck
```

Build production bundles:
```bash
npm run build
```

## Structure

```
src/
  entries/       ← per-page entry points (one per Flask page)
  components/    ← Vue single-file components (.vue)
  composables/   ← shared Vue composables (useXxx.ts)
  api/           ← typed fetch adapters for Flask /api/... endpoints
  types/         ← shared TypeScript interfaces and types
  styles/        ← Vue-island-scoped CSS (does NOT own global styles)
public/          ← static assets served as-is
```

## Entry Points

| File                      | Page             | Migration status       |
|---------------------------|------------------|------------------------|
| `src/entries/service.ts`  | `/service`       | First migration target |
| `src/entries/index.ts`    | `/`              | Late-stage target      |
| `src/entries/gap.ts`      | `/gap`           | Stub                   |
| `src/entries/matches.ts`  | `/matches`       | Stub                   |

## Flask Integration

Flask template wiring is **not yet done** in this scaffold.
The next step is to create `pricewatch/web/assets.py` with a Vite manifest
loader and inject the correct `<script>` tags in Jinja templates.

## Global Styles

Global visual ownership belongs to `static/css/common.css`.
`src/styles/base.css` is scoped to Vue-owned islands only.

