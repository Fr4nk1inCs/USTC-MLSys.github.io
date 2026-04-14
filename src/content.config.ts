import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    summary: z.string(),
    description: z.string().optional(),
    status: z.enum(["published", "draft"]).default("published"),
    date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
    tags: z.array(z.string()).default([]),
    tone: z.enum(["teal", "copper", "graphite"]).default("copper"),
    featured: z.boolean().default(false),
    metrics: z
      .array(z.object({ value: z.string(), label: z.string() }))
      .default([]),
    links: z.record(z.string()).default({}),
    pageLabel: z.string().default("Blog"),
    author: z.string().default(""),
    coverImage: z.string().optional(),
  }),
});

const publications = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/publications" }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    abstract: z.string().optional(),
    authors: z.array(z.string()),
    venue: z.string(),
    month: z.string().default(""),
    year: z.number().int(),
    type: z.enum(["conference", "journal", "workshop", "preprint"]),
    researchArea: z.string(),
    tags: z.array(z.string()).default([]),
    award: z.string().default(""),
    projectSlug: z.string().default(""),
    pdfUrl: z.string().default(""),
    codeUrl: z.string().default(""),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/projects" }),
  schema: z.object({
    title: z.string(),
    subtitle: z.string().optional(),
    summary: z.string(),
    description: z.string().optional(),
    category: z.string().default(""),
    status: z.string().default("active"),
    year: z.number().int().optional(),
    featured: z.boolean().default(false),
    tone: z.enum(["teal", "copper", "graphite"]).default("teal"),
    tags: z.array(z.string()).default([]),
    metrics: z
      .array(z.object({ value: z.string(), label: z.string() }))
      .default([]),
    links: z.record(z.string()).default({}),
    pageLabel: z.string().default("Project"),
  }),
});

const team = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/team" }),
  schema: z.object({
    name: z.string(),
    role: z.string(),
    group: z.enum([
      "faculty",
      "postdoc",
      "phd",
      "master",
      "engineer",
      "alumni",
    ]),
    researchInterests: z.array(z.string()).default([]),
    homepage: z.string().default(""),
    github: z.string().default(""),
    email: z.string().default(""),
    photo: z.string().optional(),
  }),
});

export const collections = { blog, publications, projects, team };
