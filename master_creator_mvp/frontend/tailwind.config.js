/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'engine': {
          '0': '#10b981',  // emerald - Unit Plan
          '1': '#3b82f6',  // blue - Lesson
          '2': '#22c55e',  // green - Worksheet
          '3': '#a855f7',  // purple - IEP Mods
          '4': '#f59e0b',  // amber - Adaptive
          '5': '#ef4444',  // red - Diagnostic
          '6': '#06b6d4',  // cyan - Feedback Loop
          'grader': '#14b8a6', // teal - Grader
          'model': '#64748b'   // slate - Student Model
        }
      }
    },
  },
  plugins: [],
}
