import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 0.0.0.0 — PC localhost và điện thoại cùng Wi‑Fi
    port: 5173,
    strictPort: true,
    allowedHosts: true, // Host LAN / IP không bị chặn DNS-rebinding
    hmr: {
      protocol: "ws",
      clientPort: 5173,
    },
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true, ws: false },
      "/uploads": { target: "http://127.0.0.1:8000", changeOrigin: true, ws: false },
    },
  },
});
