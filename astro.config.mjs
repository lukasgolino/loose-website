// @ts-check
import { defineConfig } from "astro/config";

// SITE_URL / SITE_BASE come from the deploy workflow (custom domain loosegame.com, so the base is "/").
export default defineConfig({
  site: process.env.SITE_URL || "https://loosegame.com",
  base: process.env.SITE_BASE || "/",
  trailingSlash: "always",
  build: { format: "directory" },
  devToolbar: { enabled: false },
});
