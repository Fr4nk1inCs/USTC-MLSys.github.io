import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export const GET: APIRoute = async () => {
  const [projects, blog, publications] = await Promise.all([
    getCollection('projects'),
    getCollection('blog', ({ data }) => data.status === 'published'),
    getCollection('publications'),
  ]);

  const items = [
    ...projects.map(p => ({
      type: 'project',
      title: p.data.title,
      url: `/projects/${p.id}/`,
      summary: p.data.summary,
      tags: p.data.tags,
    })),
    ...blog.map(p => ({
      type: 'blog',
      title: p.data.title,
      url: `/blog/${p.id}/`,
      summary: p.data.summary,
      tags: p.data.tags,
    })),
    ...publications.map(p => ({
      type: 'publication',
      title: p.data.title,
      url: `/publications/${p.id}/`,
      summary: p.data.summary,
      tags: p.data.tags,
    })),
  ];

  return new Response(JSON.stringify(items, null, 2), {
    headers: { 'Content-Type': 'application/json' },
  });
};
