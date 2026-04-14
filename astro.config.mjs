import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://ustc-mlsys.github.io',
  integrations: [mdx(), sitemap()],
  build: {
    format: 'directory',
  },
});
