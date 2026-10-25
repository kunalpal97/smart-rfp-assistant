
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],

  server: {
    port: 5173,
    strictPort: true,
  },

  build: {
    rollupOptions: {
      input: {
        main: fileURLToPath(new URL("./index.html", import.meta.url)),
        authPopup: fileURLToPath(
          new URL("./auth-popup.html", import.meta.url)
        ),
      },
    },
  },
});
