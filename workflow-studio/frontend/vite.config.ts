import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 1993,
    proxy: {
      '/api': {
        target: 'http://localhost:1994',
        changeOrigin: true,
      },
    },
  },
})
