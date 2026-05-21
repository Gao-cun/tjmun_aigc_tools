import type { Config } from "tailwindcss";
import animate from "tailwindcss-animate";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#080A0F",
        foreground: "#F4F7FB",
        muted: "#8993A5",
        border: "rgba(148, 163, 184, 0.18)",
        panel: "#0E1118",
        panelSoft: "#141923",
        accent: "#56C2FF",
        success: "#39D98A",
        warning: "#F4C95D",
        danger: "#FF6B6B"
      },
      boxShadow: {
        panel: "0 24px 80px rgba(0, 0, 0, 0.28)"
      }
    }
  },
  plugins: [animate]
};

export default config;
