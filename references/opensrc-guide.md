# opensrc Guide

How to use opensrc for dependency source analysis during code cannibalization.

## Table of Contents
1. [What is opensrc](#what-is-opensrc)
2. [Installation](#installation)
3. [Core Pattern](#core-pattern)
4. [Use Cases](#use-cases)
5. [Integration with Cannibalizer](#integration-with-cannibalizer)

## What is opensrc

opensrc fetches dependency source code so agents can read implementations, not just types. It clones repositories at the correct version tag and caches them globally at `~/.opensrc/`.

Source: [vercel-labs/opensrc](https://github.com/vercel-labs/opensrc) (2.8K stars)

## Installation

```bash
npm install -g opensrc
```

## Core Pattern

```bash
# Get path to cached source
opensrc path <package-name>

# Example
opensrc path zod          # prints: ~/.opensrc/zod@3.23.8
opensrc path prisma       # prints: ~/.opensrc/prisma@5.19.0
opensrc path next         # prints: ~/.opensrc/next@14.2.0
```

If not cached, opensrc fetches automatically. Progress goes to stderr, path to stdout.

## Use Cases

### Search dependency internals

```bash
# Find how zod parses schemas
rg "parse" $(opensrc path zod)

# Find how prisma generates types
rg "generate" $(opensrc path prisma) --type ts
```

### Read specific files

```bash
# Read zod's type definitions
cat $(opensrc path zod)/src/types.ts

# Read prisma's client implementation
cat $(opensrc path prisma)/src/runtime/index.ts
```

### Study test patterns

```bash
# Find all tests in zod
find $(opensrc path zod) -name "*.test.ts"

# Read a specific test
cat $(opensrc path zod)/src/__tests__/parse.test.ts
```

### Compare two libraries

```bash
# Compare zod vs yup structure
find $(opensrc path zod) -name "*.ts" | head -20
find $(opensrc path yup) -name "*.ts" | head -20
```

## Integration with Cannibalizer

### Phase 5: Map + Analyze

When analyzing repos, use opensrc to understand their dependencies:

```bash
# 1. Check what a repo depends on
cat ./workspace/repo/package.json | jq '.dependencies'

# 2. Fetch source of interesting dependencies
opensrc path zod
opensrc path trpc

# 3. Study how the repo uses them
rg "import.*zod" ./workspace/repo/src/
rg "from.*trpc" ./workspace/repo/src/

# 4. Read the actual implementation
cat $(opensrc path zod)/src/index.ts
```

### When to Use opensrc

Use opensrc when:
- A repo uses a library in a clever way you want to replicate
- You need to understand the internal patterns of a key dependency
- You're deciding between two similar libraries
- You want to understand how a library implements a feature

### When NOT to Use opensrc

Skip opensrc when:
- The repo's code is self-contained (no interesting deps)
- The dependency is simple (lodash, moment)
- You already know how the dependency works
- Time is critical and you need to move fast

### Speed Tip

opensrc caches globally. After first fetch, subsequent uses are instant:
```bash
# First time: fetches from GitHub (slow)
opensrc path zod

# Later: instant (cached)
opensrc path zod
```
