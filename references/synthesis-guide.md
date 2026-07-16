# Synthesis Guide

How to combine code from multiple repositories into one working codebase.

## Table of Contents
1. [Core Philosophy](#core-philosophy)
2. [Copy Files](#copy-files)
3. [Extract Code Blocks](#extract-code-blocks)
4. [Replicate Patterns](#replicate-patterns)
5. [AI Fills Gaps](#ai-fills-gaps)
6. [Architecture Selection](#architecture-selection)
7. [Type System Unification](#type-system-unification)
8. [Error Handling Merge](#error-handling-merge)
9. [Naming Convention](#naming-convention)
10. [Quality Checklist](#quality-checklist)

**Audience:** This guide is for an AI agent executing code synthesis. All instructions are direct commands.

## Core Philosophy

"Copy from one, it's theft. Copy from a thousand, it's creation."

We don't copy everything. We harvest the best from many sources and synthesize something new:
1. **Copy files** — configs, utils, simple modules (direct copy)
2. **Extract code blocks** — components, functions, classes (copy what's useful)
3. **Replicate patterns** — understand + rebuild (not verbatim copy)
4. **Write missing code** — generate what no repo covers

## Copy Files

Direct copy works for:
- **Configs**: package.json, tsconfig.json, .env.example, .eslintrc
- **Utils**: simple helper functions, constants, types
- **Templates**: boilerplate structures, README templates
- **Assets**: icons, fonts, static files

```bash
# Copy configs that work
cp ./workspace/repo1/package.json ./output/package.json
cp ./workspace/repo1/tsconfig.json ./output/tsconfig.json
cp ./workspace/repo1/.env.example ./output/.env.example
cp ./workspace/repo1/.eslintrc.js ./output/.eslintrc.js
```

**When to copy directly:**
- The file is self-contained (no dependencies on other repo files)
- The file is generic (works in any project)
- The file is simple (< 100 lines)
- The file is a config or template

**When NOT to copy directly:**
- The file imports from other repo files
- The file has repo-specific logic
- The file is complex (> 200 lines)
- The file has hardcoded values

## Extract Code Blocks

Copy specific functions, classes, or components from larger files:

```typescript
// Source: ./workspace/repo1/src/utils/validation.ts
// We only need the validateEmail function

export function validateEmail(email: string): boolean {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}
```

**How to extract:**
1. Read the source file
2. Identify the function/class/component you need
3. Copy just that block
4. Adapt imports to your project
5. Adapt types to your unified type system

**Extraction checklist:**
- [ ] All dependencies identified
- [ ] Imports adapted to your project
- [ ] Types adapted to your unified types
- [ ] Error handling converted
- [ ] Naming convention applied

## Replicate Patterns

Understand how a repo solves a problem, then rebuild it for your use case:

```
Source Pattern (from repo1):
  - Uses a middleware pattern for auth
  - Each middleware is a function that takes (req, res, next)
  - Middlewares are chained in order

Our Implementation:
  - Same middleware pattern
  - But with our auth types
  - And our error handling
  - And our naming conventions
```

**When to replicate (not copy):**
- The code is tightly coupled to the repo
- The code uses repo-specific types
- The code has complex dependencies
- You want to improve the implementation

**How to replicate:**
1. Read the source code
2. Understand the pattern (not the code)
3. Rebuild with your types and conventions
4. Add your improvements

## Write Missing Code

When no repo covers a feature, write it from scratch:

```typescript
// Gap: No repo has a good useLocalStorage hook
// Write it:

import { useState, useEffect } from 'react';

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      window.localStorage.setItem(key, JSON.stringify(storedValue));
    } catch (error) {
      console.error(error);
    }
  }, [key, storedValue]);

  return [storedValue, setStoredValue] as const;
}
```

**When to write new code:**
- No repo covers the feature
- Existing implementations are poor quality
- A custom solution is needed
- Multiple patterns need integration

**Writing rules:**
- Follow the patterns from the best repos
- Use the unified type system
- Use the dominant naming convention
- Include error handling
- Include basic tests

## Architecture Selection

Pick the architecture from the highest-quality repo:
- Has the most features you need
- Uses the cleanest structure
- Has the best test coverage
- Uses your target language/framework

**Decision framework:**
- Feature exists in 1 repo → use that implementation
- Feature exists in 2+ repos → use the one from highest-quality repo
- Feature exists in 2+ repos with similar quality → use the simpler one
- Feature doesn't exist → write it from scratch

## Type System Unification

When repos use different data models:

```
Repo A: User { id, name, email }
Repo B: Account { userId, username, emailAddress }
→ Unified: User { id: string, name: string, email: string }
```

**Rules:**
1. Map equivalent types across repos
2. Create unified interfaces combining best fields
3. Keep the simpler type when fields are equivalent
4. Add types for gaps (write them)

## Error Handling Merge

Best patterns in order of preference:
1. **Result types** (Rust-style) — explicit, composable
2. **Custom error classes** — typed, catchable
3. **Error boundaries** (React) — UI resilience
4. **Try/catch** — standard, works everywhere

**When patterns conflict:**
- Use the pattern from the highest-quality repo
- Convert other repos' error handling to match
- Document the conversion in synthesis report

## Naming Convention

Use the dominant convention across source repos:
1. Count occurrences of each convention
2. Use the most common one
3. Convert all code to match

**If conventions split 50/50:**
- Use the convention native to your target language
- Python → snake_case
- JavaScript/TypeScript → camelCase (variables/functions), PascalCase (classes)

## Quality Checklist

After synthesis, verify:

- [ ] All features from target product are covered
- [ ] No security issues carried over (check security_scanner output)
- [ ] Consistent naming conventions throughout
- [ ] Types/interfaces unified across sources
- [ ] Error handling consistent
- [ ] Tests cover extracted components
- [ ] README explains architecture decisions
- [ ] SYNTHESIS_REPORT.md documents all sources and decisions
- [ ] Project runs without errors (`npm install && npm run dev`)
