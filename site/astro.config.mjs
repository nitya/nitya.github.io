// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// This repo is a user/organization GitHub Pages repo (nitya.github.io),
// so the site publishes at the domain root and needs no `base` path.
export default defineConfig({
  site: "https://nitya.github.io",
  integrations: [sitemap()],
  build: {
    // Inline all CSS into each page's <head> so styles are render-blocking and
    // arrive with the HTML. Prevents a flash of unstyled content (FOUC) on
    // mobile page navigation, where an external stylesheet can load after paint.
    inlineStylesheets: "always",
  },
});
