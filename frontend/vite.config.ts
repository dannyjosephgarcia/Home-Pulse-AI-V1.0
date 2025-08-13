import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Export a function instead of using top-level variables
export default defineConfig(({ mode }) => {
  const isProd = mode === 'production';

  return {
    base: isProd ? '/Home-Pulse-AI-V1.0/' : '/',
    plugins: [react()]
  };
});
