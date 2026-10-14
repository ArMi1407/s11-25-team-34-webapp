import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables based on the current mode
  const env = loadEnv(mode, process.cwd(), '');
  return {
    // Vite plugins
    plugins: [react(), tailwindcss()],
    server: {
      // Uses VITE_PORT or defaults to 5173
      port: parseInt(env.VITE_PORT) || 5173,
      host: true, // Allows access from Docker
      watch: {
        usePolling: true, // To detect changes in Docker
      },
    },
    // Define global constants
    define: {
      __APP_NAME__: JSON.stringify(env.VITE_APP_NAME),
      __APP_ENV__: JSON.stringify(env.VITE_NODE_ENV),
    },
  };
});
