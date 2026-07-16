---
name: code-cannibalizer:pattern-analyst
description: "Deep pattern analysis across multiple repositories. Detects naming conventions, architecture patterns, code idioms, anti-patterns, and quality signals. Use after cloning and mapping repos to understand what works and what to copy."
argument-hint: "[repo_paths or maps] -- e.g., 'analyze patterns in ./workspace/*', 'what patterns do these repos use'"
license: MIT
metadata:
  author: michiel
  version: "2.0.0"
  scope: code-cannibalizer
---

# Pattern Analyst

Analyze code patterns across multiple repositories to find what works, what's common, and what's best.

## When to Use

- After cloning and mapping repos
- User asks "what patterns do these repos use?"
- Before synthesis to understand best practices
- User says "analyze patterns", "what's the architecture", "find best practices"

## Quick Start

```bash
# Map repos first
python3 scripts/repo_mapper.py ./workspace/repo1 -o maps/repo1.json
python3 scripts/repo_mapper.py ./workspace/repo2 -o maps/repo2.json

# Analyze patterns across mapped repos
python3 scripts/pattern_analyzer.py maps/*.json -o pattern_analysis.json
```

## What We Detect

- **Naming conventions**: snake_case, camelCase, PascalCase, kebab-case
- **Architecture patterns**: modular, flat, layered, library, CLI, monorepo
- **Code idioms**: error handling, auth, validation, state management
- **Anti-patterns**: god files, god classes, deep nesting, dead code
- **Quality signals**: tests, types, docs, CI, linting

## Detailed Analysis

For the full analysis dimensions, scoring system, decision framework, and output format, read `agents/pattern-analyst.md`.

## Pattern Vocabulary

For the complete pattern catalog, read `references/pattern-vocabulary.md`.

## Decision Framework

When patterns conflict:
1. Prefer the pattern from the highest-quality repo (stars + tests + docs)
2. Prefer the pattern used by the majority (consensus)
3. Prefer the pattern that's easier to maintain (simplicity)
4. If still tied, pick the one that matches the target language's conventions
