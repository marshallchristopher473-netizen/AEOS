import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'node:url';

export default defineConfig({
  test: {
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    // Each test file builds its own in-memory / temp-file database, so the
    // default parallel pool is safe.
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '@db': fileURLToPath(new URL('./db', import.meta.url)),
    },
  },
});
