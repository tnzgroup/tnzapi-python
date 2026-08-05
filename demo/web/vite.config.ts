import { fileURLToPath } from 'node:url'
import path from 'node:path'
// vitest/config re-exports Vite's defineConfig with the `test` field typed in, so Vitest's
// settings can live in this same file instead of a separate vitest.config.ts — it still produces
// a plain Vite config for `vite`/`vite build` to consume, this import only adds types.
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const srcDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), './src')

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': srcDir,
    },
  },
  server: {
    port: 5373,
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY_TARGET ?? 'http://localhost:5080',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.{ts,tsx}'],
    globals: false,
  },
})
