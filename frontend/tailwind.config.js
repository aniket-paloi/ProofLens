/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        stoic: {
          canvas: "#FBFBF9",
          card: "#FFFFFF",
          dark: "#121212",
          darkCard: "#18181A",
          subtle: "#F4F4F2",
          border: "#E8E8E6",
          text: "#18181B",
          secondary: "#52525B",
          muted: "#71717A",
          terracotta: "#B45309",
          terracottaLight: "#FEF3C7",
          sage: "#047857",
          sageLight: "#D1FAE5",
          rose: "#B91C1C",
          roseLight: "#FEE2E2",
        }
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "SF Pro Text",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
}

