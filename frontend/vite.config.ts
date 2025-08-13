import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const isGithubPages = process.env.NODE_ENV === 'production';

export default defineConfig({
  base: isGithubPages ? '/Home-Pulse-AI-V1.0/' : '/',
  plugins: [react()],
  server: {
    historyApiFallback: true
  }
});
