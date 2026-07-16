---
name: code-cannibalizer:code-simplifier
description: "Post-synthesis code cleanup. Flattens nesting, extracts repeated patterns, improves naming, removes dead code, and ensures consistent style. Use after synthesizing code from multiple repos to clean up the result without changing behavior."
argument-hint: "[code_path] -- e.g., 'simplify ./src', 'clean up the synthesized code'"
license: MIT
metadata:
  author: michiel
  version: "2.0.0"
  scope: code-cannibalizer
---

# Code Simplifier

Clean up synthesized code after the cannibalizer combines patterns from multiple repos.

## When to Use

- After synthesizing code from multiple repos
- Code has redundant patterns from different sources
- Inconsistent naming from merged conventions
- Over-engineered solutions copied from larger projects
- User says "simplify", "clean up", "make this cleaner"

## Rules

1. **Never change behavior** — only improve readability and structure
2. **Preserve all functionality** — every feature must still work
3. **Keep the architecture** — don't restructure, just clean up
4. **Document decisions** — note what you changed and why

## Quick Checklist

- Flatten nesting (extract early returns, guard clauses)
- Extract repeated patterns (3+ lines in 3+ places → function)
- Improve naming (`d` → `data`, `fn` → `handler`)
- Remove dead code (unused imports, commented-out code)
- Consolidate duplicate logic (merge near-duplicate functions)
- Simplify conditionals (extract complex conditions to variables)
- Consistent style (quotes, semicolons, indentation)

## Detailed Simplification

For the full checklist with before/after examples, read `agents/code-simplifier.md`.

## What NOT to Do

- Don't change algorithms
- Don't change data structures
- Don't change API contracts
- Don't change error messages users might depend on
- Don't "optimize" performance
- Don't add features
- Don't remove features
- Don't change the tech stack

## Output

After simplification, produce:
1. The cleaned code files
2. A brief changelog of what was simplified
