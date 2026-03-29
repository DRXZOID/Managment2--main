# Frontend Architecture

## Overview

The frontend is a **Vue 3 + Vite 5 + TypeScript SPA** served through a single
Flask-rendered shell (`templates/spa.html`). Flask owns the backend API (`/api/*`)
and serves `spa.html` for all operator-facing UI routes. Vue Router owns all
client-side navigation.

This is a SPA architecture. Flask does **not** render per-page HTML anymore — it
returns `spa.html` for every UI route and returns JSON for every `/api/*` route.

---

## SPA Entry Point

One Vite entry point — `frontend/src/main.ts`:

- Creates the Vue application, registers Pinia and Vue Router, mounts `App.vue` on `#app`.
- `App.vue` renders `AppShellLayout`, which hosts the shared header/nav and a `<RouterView>`.
- All four operator pages and the `NotFoundPage` are lazy-loaded by the router.

The manifest key is `src/main.ts` (Vite uses the source path as the key).
Flask loads it via `{{ vite_asset_tags('src/main.ts') }}` in `templates/spa.html`.

---

## Route Table

`frontend/src/router/routes.ts` declares all client-side routes:

| Path | Route name | Component |
|---|---|---|
| `/` | `comparison` | `ComparisonRouteView.vue` |
| `/service` | `service` | `ServiceRouteView.vue` |
| `/gap` | `gap` | `GapRouteView.vue` |
| `/matches` | `matches` | `MatchesRouteView.vue` |
| `/:pathMatch(.*)*` | `not-found` | `NotFoundPage.vue` |

Route `meta.title` and `meta.subtitle` are read by `AppShellHeader` to render the
per-route header band without per-page shell duplication.

### Flask ↔ Vue Router handoff

`pricewatch/web/ui_routes.py` (`ui_bp`):
- Explicit routes (`/`, `/service`, `/gap`, `/matches`, `/app/*`) → serve `spa.html`.
- `@ui_bp.app_errorhandler(404)` catch-all → serve `spa.html` for any non-`/api/` path.
- `/api/*` 404s → pass through as JSON errors.

This lets browser refreshes and direct deep-link URLs always hydrate the SPA correctly.
Vue Router then resolves the path to the correct component (or `NotFoundPage`).

---

## Application Shell

```
App.vue
└── AppShellLayout.vue
    ├── AppShellHeader.vue   ← title/subtitle from route.meta, RouterLink nav
    └── <main>
        └── <RouterView />   ← active page component mounts here
```

`AppShellHeader` reads `route.meta.title` and `route.meta.subtitle` for per-route
headings. Navigation uses `<RouterLink>` with `exact-active-class="active"` (and
`active-class=""` to suppress prefix-match highlights on the `/` link).

---

## Source Tree

```
frontend/
├── src/
│   ├── main.ts               ← SPA entry point
│   ├── App.vue               ← Root component
│   ├── router/
│   │   ├── index.ts          ← createRouter (history mode + scrollBehavior)
│   │   └── routes.ts         ← Route table + RouteMeta augmentation
│   ├── layouts/
│   │   └── AppShellLayout.vue
│   ├── pages/
│   │   ├── comparison/       ← / — comparison page
│   │   │   ├── ComparisonRouteView.vue
│   │   │   ├── ComparisonPage.vue
│   │   │   ├── api.ts
│   │   │   ├── types.ts
│   │   │   ├── components/
│   │   │   └── composables/
│   │   ├── service/          ← /service — service console
│   │   ├── gap/              ← /gap — gap review
│   │   ├── matches/          ← /matches — confirmed matches
│   │   └── NotFoundPage.vue  ← Client-side 404 (catch-all route)
│   ├── components/           ← Shared Vue components (AppShellHeader, BaseButton, …)
│   ├── composables/          ← Shared composables (useAsyncState, …)
│   ├── api/
│   │   ├── http.ts           ← Low-level typed fetch wrapper (requestJson)
│   │   ├── client.ts         ← Page-agnostic endpoint helpers
│   │   ├── errors.ts         ← ApiError class
│   │   └── adapters/         ← Response-shape normalizers
│   ├── stores/               ← Pinia stores
│   ├── types/                ← Shared DTO types
│   ├── styles/               ← Global/shared CSS imported by main.ts
│   └── test/                 ← Vitest unit and component tests
│       ├── router/           ← Router contract tests
│       ├── api/
│       ├── components/
│       ├── composables/
│       └── pages/
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json
└── package.json
```

---

## Per-Page Structure Convention

Every page module under `frontend/src/pages/<page>/` follows this layout:

```
<page>/
├── <PageName>RouteView.vue   ← Thin wrapper; registered in router/routes.ts
├── <PageName>Page.vue        ← Root component — mounts sub-components, calls composable
├── api.ts                    ← Thin wrappers for this page's backend endpoints only
├── types.ts                  ← DTO types mirroring backend API shapes for this page
├── components/               ← Components used only on this page
│   ├── shared/               ← Micro-components reused within the page
│   └── *.vue
└── composables/
    └── use<PageName>Page.ts  ← Primary page-state composable
```

---

## Composable Conventions

Page composables (`use<Page>Page.ts`) own:
- all reactive state (`ref`, `computed`);
- async data loading;
- action handlers (compare, makeDecision, etc.).

They **must not**:
- call Flask directly (that is `api.ts`'s job);
- be shared across pages.

Shared composables (`frontend/src/composables/`) are page-agnostic utilities.

---

## API Layer

`frontend/src/api/http.ts` — low-level typed `fetch` wrapper (`requestJson`). Converts non-2xx responses to `ApiError`. Never calls business logic.

`frontend/src/api/client.ts` — page-agnostic endpoint helpers (`fetchStores`, `fetchCategoriesForStore`, scheduler CRUD, mappings, etc.). Uses adapters from `api/adapters/` to normalize raw server shapes.

`frontend/src/pages/<page>/api.ts` — page-scoped thin wrappers for endpoints only that page uses.

**Rules:**
- Never use `fetch` or `axios` directly in components or composables — always go through `requestJson`.
- Never import page-specific `api.ts` from a different page's code.

---

## Flask ↔ Vite Integration

Integration is handled by `pricewatch/web/assets.py`, which exposes `vite_asset_tags(entry)` as a Jinja global.

**Dev mode** (`VITE_USE_DEV_SERVER=True`):
- Set `VITE_DEV_SERVER_URL=http://localhost:5173`.
- `vite_asset_tags('src/main.ts')` emits a `<script type="module">` tag pointing to the Vite dev server.

**Production** (`npm run build`):
- Vite writes hashed assets to `static/dist/` and a manifest to `static/dist/.vite/manifest.json`.
- `vite_asset_tags('src/main.ts')` reads the manifest and emits correct `<link>` + `<script>` tags.

**Jinja usage in `spa.html`:**
```html
{{ vite_asset_tags('src/main.ts') }}
```

---

## Static Assets Policy

| Path | Purpose |
|---|---|
| `static/css/common.css` | **Active** — shared `app-shell-*` styles loaded by `spa.html`. |
| `static/dist/` | **Generated** — Vite build output; not committed. |

---

## Testing

Frontend tests use **Vitest** and **@vue/test-utils**.

```bash
cd frontend
npm test                          # run all tests once
npm test -- --reporter=verbose    # with per-test output
npm run typecheck                 # vue-tsc --noEmit
npm run build                     # full type check + production build
```

| Test path | What it covers |
|---|---|
| `test/router/` | Router contract: canonical routes, catch-all, route meta |
| `test/api/` | `requestJson`, `ApiError` |
| `test/components/` | Shared Vue components including `AppShellHeader` |
| `test/composables/` | Shared composables |
| `test/pages/comparison/` | Comparison page composable and components |
| `test/pages/gap/` | Gap page composable and components |
| `test/pages/matches/` | Matches page composable and components |
| `test/pages/service/` | Service page tabs and components |
| `test/pages/NotFoundPage.test.ts` | NotFound screen structure and path display |

---

## Guardrails

- **Flask owns `/api/*`** — never navigate to API routes from Vue components.
- **Vue Router owns UI navigation** — use `<RouterLink>` or `router.push()`, never `window.location`.
- **No inline `onclick` handlers** in `spa.html`. All interactions are Vue-owned.
- **No `window.*` global action handlers.** All interactivity is component-scoped.
- **Do not import page `api.ts` across pages.** Shared API helpers belong in `frontend/src/api/client.ts`.

---

## Mutation UX Policy

After any data mutation (confirm/reject match, gap status change, delete row):

> **Do not blank visible page content.** Keep current data on screen until the replacement arrives.

| Page | Mutation | Implementation |
|---|---|---|
| `/` (comparison) | confirm / reject | `makeDecision()` calls `_runComparison()` without clearing `comparisonResult` first |
| `/gap` | status change | `patchGapItemStatus()` updates item + recalculates summary locally |
| `/matches` | delete row | Row removed locally from `rows` + `total` decremented |
