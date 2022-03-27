# Setup using Docusaurus

This site is built with [Docusaurus v2](https://docusaurus.io/) a React-based framework for building optimized websites. This makes it a good sandbox to explore richer web experiences later.p

 * Write content in Markdown
 * Use [MDX](https://mdxjs.com/) to embed React components in Markdown
 * Support for localization
 * Support for search
 * Built-in support for tutorials, blog posts

<br/><br/>

---

## Setup

* Install Node.js - I'm using v16.14 at setup time. 
* The source content is in `www` and site will be deployed to GitHub pages, ideally with GitHub Actions setup. 
* Check [package.json](www/package.json) for other script commands.

| Command | Description |
|:---|:---|
| `npx create-docusaurus@latest www classic` | Scaffold site in `www/` folder|
| `npm start` | Start dev server with hot reload |
| `npm run build` | Build production-ready static files |
| `npm run serve` | Serve built site locally clear|
| `npm deploy` | Publishes site to GitHub pages|
| | |

<br/><br/>

---

## Deployment to GitHub Pages

* Configure [docusaurus.config.js](www/docusaurus.config.js) as described [here](https://docusaurus.io/docs/deployment#deploying-to-github-pages)
* Use `npm deploy` to deploy manually.
* Follow [these steps](https://docusaurus.io/docs/deployment#triggering-deployment-with-github-actions) to automate with GitHub Actions



<br/><br/>

---

## Create Content

<br/>

> **Standalone pages**

Ex: About page.

 * Created under `src/pages`
 * `src/pages/x/y` hsoted at `<site>/x/y` route 
 * Create content as Markdown (.md) or React (.js)
<br/><br/>

> **Document pages**

Collection of pages that are connected by a _sidebar_ with built-in _prev/next_ navigational cues. 

Ex: tutorials

 * Created under `docs`
 * `docs/hello.md` hosted at `<site>/docs/hello` route
 * Sidebar configured automatically by default
 * Configure explicitly using `sidebars.js`
 * Use frontmatter in file to customize sidebar label/position.

See: [Docs Frontmatter](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-content-docs#markdown-front-matter)
<br/><br/>

> **Blog**

Blog posts have datestamps, a blog index page, a tag system and an RSS feed.

[See Blog Guide](https://docusaurus.io/docs/blog)

 * Create under `blog/`
 * Update frontmatter in blog post
 * Filename as default for date/slug
 * Define [authors](https://docusaurus.io/docs/blog#blog-post-authors) inline or in global [authors.yml](www/blog/authors.yml) file.

See [Blog Frontmatter](https://docusaurus.io/docs/api/plugins/@docusaurus/plugin-content-blog#markdown-front-matter)
<br/><br/>

> **Markdown Formatting**

 * Support for rich [Markdown features](https://docusaurus.io/docs/markdown-features)
 * Use [MDX](https://docusaurus.io/docs/markdown-features/react) to embed React components
 * Use [Tabs](https://docusaurus.io/docs/markdown-features/tabs) for parallel snippets
 * Use [Codeblocks](https://docusaurus.io/docs/markdown-features/code-blocks) with highlighting
 * Use [Admonitions](https://docusaurus.io/docs/markdown-features/admonitions) for highlighting remarks
 * Rich [frontmatter](https://docusaurus.io/docs/docs-markdown-features#markdown-front-matter) support
 * Standard [Headings](https://docusaurus.io/docs/markdown-features/headings)
 * Inline [Table Of Contents](https://docusaurus.io/docs/markdown-features/inline-toc)
 * Display [Assets](https://docusaurus.io/docs/markdown-features/assets) incl. themed images
 * Explore [plugins](https://docusaurus.io/docs/markdown-features/plugins) for custom formats
 * Use KaTeX for [Math Equations](https://docusaurus.io/docs/markdown-features/math-equations)
 * Set [Head Metadata](https://docusaurus.io/docs/markdown-features/head-metadata) for SEO.

<br/>

> Additional Guides

 * [Pages](https://docusaurus.io/docs/creating-pages)
 * [Docs](https://docusaurus.io/docs/docs-introduction)
 * [Blog](https://docusaurus.io/docs/blog)
 * [Markdown Features](https://docusaurus.io/docs/markdown-features)
 * [Styling and Layout](https://docusaurus.io/docs/styling-layout)
 * [Swizzling](https://docusaurus.io/docs/swizzling)
 * [Static Assets](https://docusaurus.io/docs/static-assets)
 * [Search](https://docusaurus.io/docs/search)
 * [Browser Support](https://docusaurus.io/docs/browser-support)
 * [SEO](https://docusaurus.io/docs/seo)
 * [Using Plugins](https://docusaurus.io/docs/using-plugins)
 * [Deployment](https://docusaurus.io/docs/deployment)
 * [Internationalization](https://docusaurus.io/docs/i18n/introduction)

 Also look at their [Showcase](https://docusaurus.io/showcase) page and the [source behind it](https://github.com/facebook/docusaurus/tree/main/website/src/pages/showcase) to understand how richer pages can be created with React components.

 ---