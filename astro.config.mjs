// @ts-check
import { defineConfig } from "astro/config";

// Hosted on GitHub Pages (lukasgolino.com/loose-website/ until it gets its own domain); the deploy workflow passes
// SITE_URL / SITE_BASE from configure-pages.
export default defineConfig({
  site: process.env.SITE_URL || "https://lukasgolino.com",
  base: process.env.SITE_BASE || "/loose-website/",
  trailingSlash: "always",
  build: { format: "directory" },
  devToolbar: { enabled: false },
});
