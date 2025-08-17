// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    // Explicitly point to frontend/index.html (no leading space!)
    rollupOptions: { input: path.resolve(__dirname, 'index.html') },
  },
})


