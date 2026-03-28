import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
//
// Multi-entry configuration for PriceWatch Flask-hosted pages.
// Each entry maps to one page rendered by Flask/Jinja.
// Output is prepared for later integration into Flask static folder —
// no manifest loading code is wired into Flask templates yet.
//
// To integrate with Flask later, set:
//   build.outDir = '../static/dist'
//   build.manifest = true
// and create pricewatch/web/assets.py for manifest lookup.

export default defineConfig({
  plugins: [vue()],

  // Base public path — must match where Flask serves static/dist/.
  // Without this Vite emits dynamic import URLs as /assets/... which 404
  // because Flask serves them from /static/dist/assets/...
  base: '/static/dist/',

  build: {
    // Output to Flask's static directory so it can serve assets directly.
    // Vite 5 writes the manifest to <outDir>/.vite/manifest.json
    // → static/dist/.vite/manifest.json (matches VITE_MANIFEST_PATH default in app_factory.py)
    outDir: '../static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        service: resolve(__dirname, 'src/entries/service.ts'),
        index: resolve(__dirname, 'src/entries/index.ts'),
        gap: resolve(__dirname, 'src/entries/gap.ts'),
        matches: resolve(__dirname, 'src/entries/matches.ts'),
      },
    },
  },

  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
})

