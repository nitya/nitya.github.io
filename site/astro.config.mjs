// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// This repo is a user/organization GitHub Pages repo (nitya.github.io),
// so the site publishes at the domain root and needs no `base` path.
export default defineConfig({
  site: "https://nitya.github.io",
  integrations: [sitemap()],
});
