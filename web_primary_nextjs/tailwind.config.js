/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0070f3",
          50: "#e0f2ff",
          100: "#b8e5ff",
          200: "#8cd8ff",
          300: "#5acaff",
          400: "#36bbff",
          500: "#0070f3",
          600: "#0065d5",
          700: "#0052b3",
          800: "#003e91",
          900: "#002a70",
        },
        secondary: {
          DEFAULT: "#7928CA",
          50: "#f5e8ff",
          100: "#e5c8ff",
          200: "#d5a5ff",
          300: "#c583ff",
          400: "#b561ff",
          500: "#7928CA",
          600: "#6b20b5",
          700: "#561a9f",
          800: "#421489",
          900: "#2d0e74",
        },
      },
    },
  },
  plugins: [],
}; 