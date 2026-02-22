/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        medical: {
          navy: '#1e3a5f',
          'navy-light': '#2d5a8e',
          teal: '#0891b2',
          'teal-light': '#22d3ee',
          light: '#f0f9ff',
          bg: '#f8fafc',
          danger: '#dc2626',
          'danger-light': '#fecaca',
          warning: '#f59e0b',
          'warning-light': '#fef3c7',
          success: '#10b981',
          'success-light': '#d1fae5',
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"Segoe UI"', 'system-ui', '-apple-system', 'sans-serif'],
      },
      borderWidth: {
        3: '3px',
      },
    },
  },
  plugins: [],
}
