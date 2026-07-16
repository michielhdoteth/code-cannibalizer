---
name: code-cannibalizer
description: >
  Clone repos super fast, security-scan them, harvest the best patterns, and
  synthesize a working codebase. Drop a link or describe what you want to build.
  Minimum 5 repos, evolves each iteration. Use when user mentions "cannibalize",
  "find repos", "build something like", "open source alternatives", or wants to
  combine code from multiple repositories. Do NOT use for single-repo tasks.
license: MIT
compatibility: opencode
metadata:
  workflow: code-synthesis
  audience: developers
  version: 3.1.0
---

# Code Cannibalizer

"Copy from one, it's theft. Copy from a thousand, it's creation."

## When to Load

- User drops a URL: "build me something like this"
- User describes a product/startup idea
- User says "cannibalize", "find repos", "open source alternatives"
- User wants to combine code from multiple repositories

## When NOT to Load

- Single-repo tasks, code review, bug fixing, documentation only

## CRITICAL CONSTRAINT

**You MUST produce a working, runnable application.** The app must have a package.json (or equivalent) and install/build without errors. SYNTHESIS_REPORT.md is SECONDARY. If you run out of context, the app must exist even if the report is incomplete.

**RULE: After writing 3+ markdown files, STOP analyzing and START coding.**

## Workflow

### Phase 1: Discover + Pre-Secure

Parse the user's intent. Run 5+ parallel websearch queries to find repos. Use GitHub API, gh CLI, opensrc. Rank by stars + recency. Keep 5-30 candidates.

Run pre-clone security on all candidates:
```bash
python3 scripts/pre_clone_scanner.py <repo_url>
```

- Trust score >= 60: proceed
- Trust score 40-59: flag, proceed with caution
- Trust score < 40: block, do not clone

Pick the top 5 safe repos for synthesis.

### Phase 2: Clone + Build

Clone the top 5 repos (`--depth 1`). Deep scan each:
```bash
python3 scripts/security_scanner.py ./workspace/<repo_name>
```

Map repo structure:
```bash
python3 scripts/repo_mapper.py ./workspace/<repo_name>
```

Analyze patterns across repos:
```bash
python3 scripts/pattern_analyzer.py ./workspace/repo1 ./workspace/repo2 ...
```

**Then BUILD THE APP.** Read `references/synthesis-guide.md` for the synthesis methodology:

1. **Copy** configs and simple utilities directly from repos
2. **Extract** specific components, functions, classes from source files
3. **Replicate** patterns — understand how a repo solves a problem, rebuild it with your types
4. **Write** all missing pieces — components no repo covers, glue code, integrations

Read `agents/pattern-analyst.md` during synthesis for pattern conflict resolution.

### Phase 3: Document

After the app works, write documentation:
- SYNTHESIS_REPORT.md (use `assets/synthesis-report-template.md`)
- ARCHITECTURE.md explaining decisions
- Security findings in `security/` folder

Use `agents/code-simplifier.md` to clean up the final code if needed.

## Routing

| Phase | Read |
|-------|------|
| 1 (if user is vague) | `agents/startup-analyst.md` |
| 2 (security rules) | `agents/security-auditor.md` |
| 2 (pattern conflicts) | `agents/pattern-analyst.md` |
| 3 (cleanup) | `agents/code-simplifier.md` |
| 2 (synthesis) | `references/synthesis-guide.md` |
| 2 (dependency analysis) | `references/opensrc-guide.md` |
| 2 (security patterns) | `references/security-patterns.md` |

## Scripts

| Script | Purpose |
|--------|---------|
| `pre_clone_scanner.py` | Trust scoring 0-100 before download |
| `security_scanner.py` | Deep scan 40+ malware patterns |
| `repo_mapper.py` | AST structure extraction |
| `pattern_analyzer.py` | Cross-repo pattern detection |

## Project Structure

All cannibalized artifacts live in `.cannibalized/` at the project root:

```
.cannibalized/
├── gitclones/              # All cloned repos (--depth 1)
│   ├── repo-name-1/
│   ├── repo-name-2/
│   └── ...
├── maps/                   # Repo structure maps (JSON for machines + MD for humans)
│   ├── repo-name-1.json
│   ├── repo-name-1.md
│   └── ...
├── security/               # Security scan results
│   ├── repo-name-1.json
│   └── ...
├── patterns/               # Pattern analysis results
│   ├── cross-repo-analysis.json
│   └── ...
├── reports/                # SYNTHESIS_REPORT.md per iteration
│   └── iteration-1/
└── workspace/              # Eval workspace (for skill testing)
    └── iteration-1/
        ├── eval-name/
        │   ├── with_skill/outputs/
        │   └── without_skill/outputs/
        └── ...
```

Everything in `.cannibalized/` is gitignored except the final synthesized output.

## Speed

Parallel everything. Copy what works. Extract what's useful. Write what's missing. Always output working code.

## Evolution

Start at 5 repos. Evaluate. Add more. Repeat. Each iteration gets better.
