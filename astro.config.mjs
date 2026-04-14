import { defineConfig } from "astro/config";
import mdx from "@astrojs/mdx";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://test.fr4nk1in.top",
  integrations: [mdx(), sitemap()],
  build: {
    format: "directory",
  },
});
