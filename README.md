# Code Cannibalizer

"Copy from one, it's theft. Copy from a thousand, it's creation."

An OpenCode skill that clones repos, security-scans them, harvests the best patterns, and synthesizes a working codebase from multiple open-source sources.

## What It Does

- Discovers relevant open-source repos for any product/startup idea
- Security-scans repos before cloning (trust scoring + deep malware detection)
- Extracts patterns, architecture, and code from multiple sources
- Synthesizes a working, runnable application from the best patterns
- Generates a SYNTHESIS_REPORT.md documenting all sources and decisions

## Installation

### OpenCode

```bash
# Clone into your skills directory
git clone https://github.com/michiel/code-cannibalizer.git ~/.config/opencode/skills/code-cannibalizer
```

### Claude Code

```bash
# Clone into your skills directory
git clone https://github.com/michiel/code-cannibalizer.git ~/.claude/skills/code-cannibalizer
```

### Manual

Copy the `code-cannibalizer/` folder into your skills directory:
- OpenCode: `~/.config/opencode/skills/`
- Claude Code: `~/.claude/skills/`

## Usage

Describe what you want to build and the skill will:

1. Find 5+ relevant open-source repos
2. Security-scan them (trust scoring + deep scan)
3. Extract patterns and architecture
4. Build a working application
5. Document everything in SYNTHESIS_REPORT.md

### Examples

```
Cannibalize Linear.app and build me a project management tool
```

```
Find open source alternatives to Notion and build a note-taking app
```

```
I want to build something like Stripe for payments but simpler
```

## Repository Structure

```
code-cannibalizer/
├── SKILL.md              # Main skill (lean router)
├── skill.json            # Subskills manifest
├── agents/               # Specialized agent prompts
│   ├── startup-analyst.md
│   ├── security-auditor.md
│   ├── pattern-analyst.md
│   └── code-simplifier.md
├── scripts/              # Python tools
│   ├── pre_clone_scanner.py
│   ├── security_scanner.py
│   ├── repo_mapper.py
│   └── pattern_analyzer.py
├── references/           # Extended documentation
│   ├── synthesis-guide.md
│   ├── opensrc-guide.md
│   └── security-patterns.md
├── assets/               # Templates
│   ├── synthesis-report-template.md
│   └── scaffold-template.json
├── evals/                # Evaluation tests
│   └── evals.json
└── skills/               # Sub-skill SKILL.md files
    ├── startup-analyst/
    ├── security-auditor/
    ├── pattern-analyst/
    └── code-simplifier/
```

## Scripts

| Script | Purpose |
|--------|---------|
| `pre_clone_scanner.py` | Trust scoring 0-100 before download |
| `security_scanner.py` | Deep scan 40+ malware patterns |
| `repo_mapper.py` | AST structure extraction |
| `pattern_analyzer.py` | Cross-repo pattern detection |

## How It Works

The skill follows a 3-phase workflow:

1. **Discover + Pre-Secure**: Find repos, trust-score them, pick the best 5
2. **Clone + Build**: Clone repos, deep-scan, extract patterns, build the app
3. **Document**: Write SYNTHESIS_REPORT.md with sources and decisions

## License

MIT - see [LICENSE](LICENSE)

## Author

michiel
