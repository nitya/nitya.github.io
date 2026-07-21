# Nitya Narasimhan, PhD

This repository is a living experiment to create a centralized personal knowledge base for my personal and professional content based on using structured data and agentic workflows to ensure it remains consistent and complete. 

- Phase 1: Establish data files and workflows to populate them
- Phase 2: Build a static website with data - on GitHub Pages
- Phase 3: Build a dynamic website with chatbot - in the cloud.

## Data Sources

Every activity or credential must be backed by a structured data source with a defined schema. Where possible, the schema should be compliant with a canonical source for that _class_ of information. Examples:

1. **Patents** - USPTO, Google Patents or Justia citation formats
1. **Publications** - Google Scholar, ACM and IEEE citation formats
1. **Talks** - Sessionize, SpeakerDeck citation formats
1. **Projects** - LinkedIn and GitHub citation formats
1. **Profile** - LinkedIn and GitHub citation formats

## Human Experience

The data powers a website that serves as the user-interface for human visitors. In phase 1, the focus is just rendering the content with meaningful routes. In phase 2, we can add richer features like search, sort and dark mode. In phase 3, we add dynamic integrations.

The website should support standards like [OpenGraph](https://ogp.me/) that allow it to become a rich object in a social graph - and take advantage of capabilities like [oembed](https://oembed.com/) to support richer content presentation when the link is cited elsewhere.

## Agent Experience

The structured data formats should be accessible over a basic GitHub MCP server connection (generic) and the site should be equipped with an AGENTS.md (for coding agents) and an llms.txt (for search agents) along with custom skills and MCP servers to support effective usage. The repository may also have agentic workflows that can run async to keep data up-to-date or support other maintenance.