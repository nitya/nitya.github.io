import { defineCollection, z } from "astro:content";
import { file } from "astro/loaders";

// Structured data lives in the repo-root `data/` folder and is the single
// source of truth. Each collection maps 1:1 to a JSON file (array of items).
// Schemas mirror external canonical sources and map to schema.org types.

const patents = defineCollection({
  loader: file("../data/patents.json"),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    abstract: z.string().optional(),
    inventors: z.array(z.string()).default([]),
    assignee: z.string().optional(),
    filingDate: z.string().optional(),
    grantDate: z.string().nullable().optional(),
    status: z.enum(["granted", "pending", "expired"]).default("pending"),
    url: z.string().url(),
    tags: z.array(z.string()).default([]),
  }),
});

const publications = defineCollection({
  loader: file("../data/publications.json"),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    authors: z.array(z.string()).default([]),
    venue: z.string().optional(),
    year: z.number().int(),
    type: z.enum(["journal", "conference", "book", "preprint"]).default("conference"),
    doi: z.string().nullable().optional(),
    url: z.string().url(),
    abstract: z.string().optional(),
    citationCount: z.number().int().nullable().optional(),
    tags: z.array(z.string()).default([]),
  }),
});

const talks = defineCollection({
  loader: file("../data/talks.json"),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    event: z.string(),
    date: z.string(),
    location: z.string().nullable().optional(),
    url: z.string().url(),
    slidesUrl: z.string().url().nullable().optional(),
    videoUrl: z.string().url().nullable().optional(),
    description: z.string().optional(),
    tags: z.array(z.string()).default([]),
  }),
});

const projects = defineCollection({
  loader: file("../data/projects.json"),
  schema: z.object({
    id: z.string(),
    name: z.string(),
    description: z.string(),
    role: z.string().nullable().optional(),
    url: z.string().url().nullable().optional(),
    repo: z.string().url().nullable().optional(),
    tech: z.array(z.string()).default([]),
    startDate: z.string().nullable().optional(),
    endDate: z.string().nullable().optional(),
    status: z.enum(["active", "archived", "completed"]).default("active"),
    tags: z.array(z.string()).default([]),
  }),
});

export const collections = { patents, publications, talks, projects };
