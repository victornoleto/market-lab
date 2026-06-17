import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Dev: proxy API calls to the FastAPI backend on :8000. Prod build is served by
// FastAPI's StaticFiles mount, so the /api paths resolve same-origin.
export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
  build: { outDir: "dist", emptyOutDir: true },
});
