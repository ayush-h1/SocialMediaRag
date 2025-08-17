import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

export default defineConfig({
  plugins: [react()],
  // DO NOT put leading spaces or absolute "/" in any of these
  root: '.',                   // project root is the frontend folder
  base: '/',                   // fine for SPA
  build: {
    outDir: 'dist',
    rollupOptions: {
      // Make sure input points to the real index.html in this folder
      input: path.resolve(__dirname, 'index.html'),
    },
  },
})

