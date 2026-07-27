import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}", "./src/app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ed: {
          orange: "#e67e22",
          dark: "#0a0a0f",
          panel: "#12121a",
          border: "#1e1e2e",
          muted: "#6b6b80",
        },
      },
    },
  },
  plugins: [],
};

export default config;
