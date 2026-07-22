import { getCollection } from "astro:content";

// A common shape every data source is normalized into so the Content gallery
// can render one uniform card per item while preserving the source type.
export interface ContentItem {
  key: string;
  type: "patent" | "publication" | "talk" | "project" | "training";
  title: string;
  description: string;
  date: string | null;
  url: string;
  tags: string[];
  source: string;
  meta: string;
}

const typeLabels: Record<ContentItem["type"], string> = {
  patent: "Patent",
  publication: "Publication",
  talk: "Talk",
  project: "Project",
  training: "Training",
};

export function typeLabel(type: ContentItem["type"]): string {
  return typeLabels[type];
}

// Load every collection and normalize into a single, sortable list.
export async function getAllContentItems(): Promise<ContentItem[]> {
  const [patents, publications, talks, projects, training] = await Promise.all([
    getCollection("patents"),
    getCollection("publications"),
    getCollection("talks"),
    getCollection("projects"),
    getCollection("training"),
  ]);

  const items: ContentItem[] = [];

  for (const p of patents) {
    items.push({
      key: `patent:${p.id}`,
      type: "patent",
      title: p.data.title,
      description: p.data.abstract ?? "",
      date: p.data.grantDate ?? p.data.filingDate ?? null,
      url: p.data.url,
      tags: p.data.tags,
      source: p.data.assignee ?? "Patent",
      meta: p.data.status === "granted" ? "Granted" : "Pending",
    });
  }

  for (const p of publications) {
    items.push({
      key: `publication:${p.id}`,
      type: "publication",
      title: p.data.title,
      description: p.data.abstract ?? "",
      date: `${p.data.year}-01-01`,
      url: p.data.url,
      tags: p.data.tags,
      source: p.data.venue ?? "Publication",
      meta: String(p.data.year),
    });
  }

  for (const t of talks) {
    items.push({
      key: `talk:${t.id}`,
      type: "talk",
      title: t.data.title,
      description: t.data.description ?? "",
      date: t.data.date,
      url: t.data.url,
      tags: t.data.tags,
      source: t.data.event,
      meta: t.data.location ?? "Talk",
    });
  }

  for (const pr of projects) {
    items.push({
      key: `project:${pr.id}`,
      type: "project",
      title: pr.data.name,
      description: pr.data.description,
      date: pr.data.startDate ?? null,
      url: pr.data.url ?? pr.data.repo ?? "#",
      tags: pr.data.tags,
      source: pr.data.role ?? "Project",
      meta: pr.data.status,
    });
  }

  for (const tr of training) {
    items.push({
      key: `training:${tr.id}`,
      type: "training",
      title: tr.data.title,
      description: tr.data.description,
      date: tr.data.date ?? null,
      url: tr.data.url,
      tags: tr.data.tags,
      source: tr.data.program ?? "Training",
      meta: tr.data.program ?? "Training",
    });
  }

  // Default sort: newest first.
  items.sort((a, b) => (b.date ?? "").localeCompare(a.date ?? ""));
  return items;
}
