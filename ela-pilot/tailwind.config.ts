import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        verified: '#15803d',
        caution: '#b45309',
        unverified: '#b91c1c',
      },
    },
  },
  plugins: [],
};

export default config;
