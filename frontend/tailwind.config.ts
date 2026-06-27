import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      boxShadow: { glow: '0 0 40px rgba(34, 211, 238, 0.12)' }
    }
  },
  plugins: [],
};
export default config;
