/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          dark: '#030712',
          card: '#0f172a',
          border: '#1e293b',
          accent: '#06b6d4',
          cyan: '#22d3ee',
          teal: '#14b8a6',
          alert: '#f43f5e',
          safe: '#10b981',
          warning: '#f59e0b',
        }
      }
    },
  },
  plugins: [],
}
