import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const backendTarget = process.env.BACKEND_URL || process.env.BACKEND_INTERNAL_URL || 'http://127.0.0.1:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true
      },
      '/health': {
        target: backendTarget,
        changeOrigin: true
      },
      '/capabilities': {
        target: backendTarget,
        changeOrigin: true
      },
      '/documents': {
        target: backendTarget,
        changeOrigin: true
      }
    }
  }
});

