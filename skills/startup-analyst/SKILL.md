---
name: code-cannibalizer:startup-analyst
description: "Analyze any startup, product, or project idea. Extracts technical components, builds search queries for repo discovery, and prioritizes what to find in open source. Use when user drops a URL describing a product or explains a project they want to build."
argument-hint: "[url or description] -- e.g., 'analyze this SaaS idea', 'what repos do I need for a Notion clone'"
license: MIT
metadata:
  author: michiel
  version: "2.0.0"
  scope: code-cannibalizer
---

# Startup Analyst

Analyze what a startup, product, or project does and translate that into technical requirements for code discovery.

## When to Use

- User drops a URL and says "build me something like this"
- User describes a product/startup idea and wants to build it
- User says "analyze this", "what do I need for", "find repos for"

## Quick Start

1. Fetch the URL or parse the description
2. Extract technical components (frontend, backend, database, auth, etc.)
3. Build search queries for each component
4. Prioritize: core differentiator > table stakes > nice-to-have

## Detailed Analysis

For the full analysis workflow, component breakdown, search query patterns, and output format, read `agents/startup-analyst.md`.

## Output

Return a structured analysis with:
- What the product does (1-2 sentences)
- Technical requirements (must-have, should-have, nice-to-have)
- Search queries for each component
- Anti-patterns to avoid
