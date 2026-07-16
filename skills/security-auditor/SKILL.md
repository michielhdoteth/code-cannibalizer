---
name: code-cannibalizer:security-auditor
description: "Security gatekeeper for code cannibalization. Pre-clone trust scoring, deep malware scanning, dependency risk analysis, and synthesis security validation. Use before cloning any repo, after cloning for deep scan, or when validating synthesized code."
argument-hint: "[repo_url or repo_path] -- e.g., 'scan https://github.com/user/repo', 'check security of ./workspace/repo'"
license: MIT
metadata:
  author: michiel
  version: "2.0.0"
  scope: code-cannibalizer
---

# Security Auditor

Security gatekeeper for the code cannibalizer. Every repo must pass through you before it gets cloned, analyzed, or synthesized.

## When to Use

- Before cloning any repo (pre-clone trust scoring)
- After cloning for deep security scan
- When validating synthesized code for vulnerabilities
- User says "scan this", "check security", "is this safe"

## Quick Start

```bash
# Pre-clone trust scoring
python3 scripts/pre_clone_scanner.py <repo_url>

# Deep security scan after clone
python3 scripts/security_scanner.py ./workspace/<repo_name>
```

## Trust Score Levels

- **80-100 (SAFE)**: Clean repo, proceed
- **60-79 (CAUTION)**: Minor concerns, note but proceed
- **40-59 (RISKY)**: Suspicious, investigate before cloning
- **0-39 (DANGEROUS)**: BLOCK immediately

## Detailed Scanning

For the full scanning workflow, severity levels, report format, and decision authority, read `agents/security-auditor.md`.

## Security Patterns

For the complete pattern catalog, read `references/security-patterns.md`.

## Verdict

- SAFE TO USE → proceed to clone and analyze
- USE WITH CAUTION → document concerns, proceed
- DO NOT USE → block, report to user
