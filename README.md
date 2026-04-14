# Lab Website

Static lab homepage for MLSys @ USTC, built with [Astro.js](https://astro.build) 6 and deployed to GitHub Pages.

## Directory

- `src/content/` — site content as Markdown/MDX files (edit these)
  - `blog/` — blog posts (`.mdx`)
  - `publications/` — papers (`.md`)
  - `team/` — team members (`.md`)
  - `projects/` — research projects (`.md`)
- `src/data/site.ts` — global config (lab name, hero, nav, etc.)
- `src/components/` — Astro components
- `src/pages/` — page routes
- `src/styles/styles.css` — global CSS
- `public/` — static assets (images, fonts, JS)
- `dist/` — build output (gitignored)

## Local dev

```bash
pnpm install
pnpm dev           # http://localhost:4321
```

## Build

```bash
pnpm build         # outputs to dist/
pnpm preview       # preview the build locally
```

## Editing content

Add or edit files in `src/content/`:

```
src/content/publications/my-paper-venue-2025.md
src/content/blog/my-post.mdx
src/content/team/my-name.md
src/content/projects/my-project.md
```

Each file uses YAML frontmatter for metadata and Markdown/MDX for the body.
Global settings (lab name, hero text, featured slugs, research areas) live in `src/data/site.ts`.

## Deploy

Pushing to `main` triggers the GitHub Actions workflow (`.github/workflows/deploy-main-to-gh-pages.yml`), which builds with `withastro/action` and deploys via `actions/deploy-pages`. No separate branch needed — GitHub Pages source should be set to **GitHub Actions** in the repository settings.
