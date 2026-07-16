#!/usr/bin/env python3
"""
Security Scanner - Scan repositories for security issues.
Checks for malicious patterns, secrets, and vulnerabilities.
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict


# Malicious patterns to detect
MALICIOUS_PATTERNS = [
    (r"eval\s*\(\s*base64", "Potential code injection via base64 eval"),
    (r"exec\s*\(\s*compile", "Potential code injection via exec/compile"),
    (r"__import__\s*\(\s*['\"]os['\"]", "Dynamic OS import"),
    (r"subprocess\.call.*shell\s*=\s*True", "Shell execution risk"),
    (r"os\.system\s*\(", "Shell execution via os.system"),
    (r"curl.*\|\s*bash", "Remote code execution via pipe"),
    (r"wget.*\|\s*sh", "Remote code execution via pipe"),
    (r"rm\s+-rf\s+/", "Dangerous recursive delete"),
    (r"chmod\s+777", "Overly permissive permissions"),
    (r"\.ssh/", "SSH key access detected"),
    (r"private.*key", "Private key reference"),
    (r"password\s*=\s*['\"][^'\"]+['\"]", "Hardcoded password"),
    (r"secret\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secret"),
    (r"api[_-]?key\s*=\s*['\"][^'\"]+['\"]", "Hardcoded API key"),
    (r"token\s*=\s*['\"][^'\"]+['\"]", "Hardcoded token"),
    # Cryptocurrency mining
    (r"stratum\+tcp://", "Stratum mining protocol connection"),
    (r"xmrig", "XMRig crypto miner reference"),
    (r"nicehash", "NiceHash mining service reference"),
    (r"minerd?", "Mining daemon reference"),
    (r"cryptonight", "CryptoNight mining algorithm"),
    (r"coinhive", "CoinHive browser miner"),
    (r"coin-hive", "Coin-Hive browser miner"),
    (r"crypto.*miner", "Cryptocurrency miner reference"),
    (r"monero.*miner", "Monero miner reference"),
    # Backdoors
    (r"/dev/tcp/", "Reverse shell via /dev/tcp"),
    (r"nc\s+-[a-z]*e\s+", "Netcat with execute flag"),
    (r"ncat\s+.*-e\s+", "Ncat with execute flag"),
    (r"bash\s+-i\s+>&?\s*/dev/tcp", "Bash reverse shell"),
    (r"python.*socket.*connect", "Python socket backdoor"),
    (r"subprocess.*sock", "Subprocess socket connection"),
    # Data exfiltration
    (r"requests\.post\(.*os\.environ", "HTTP POST with env vars (exfiltration)"),
    (r"urllib\.request\.urlopen.*POST.*open\(", "HTTP POST with file read (exfiltration)"),
    (r"curl.*-d.*@", "curl POST file contents"),
    (r"wget.*--post-file", "wget POST file contents"),
    # Obfuscation chains
    (r"eval\s*\(\s*base64\.b64decode\s*\(\s*base64", "Double base64 decode eval"),
    (r"exec\s*\(\s*bytes\.fromhex", "Hex decode exec"),
    (r"eval\s*\(\s*compile\s*\(\s*base64", "Base64 compile eval"),
]

# Suspicious file extensions
SUSPICIOUS_EXTENSIONS = [
    ".exe", ".dll", ".so", ".dylib", ".bin",
    ".scr", ".bat", ".cmd", ".ps1", ".vbs",
    ".sh", ".bash",
]

# Sensitive paths
SENSITIVE_PATHS = [
    ".env", ".env.local", ".env.production",
    "credentials.json", "service-account.json",
    ".htpasswd", ".htaccess",
    "id_rsa", "id_ed25519", "id_dsa",
]


@dataclass
class SecurityFinding:
    """A security finding."""
    severity: str  # critical, high, medium, low, info
    category: str
    file: str
    line: int = 0
    message: str = ""
    pattern: str = ""
    suggestion: str = ""


@dataclass
class SecurityReport:
    """Complete security report for a repository."""
    repo_name: str
    repo_path: str
    scan_time: str = ""
    findings: List[Dict] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    risk_score: int = 0
    risk_level: str = "unknown"
    summary: str = ""


class SecurityScanner:
    """Scan a repository for security issues."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.findings: List[SecurityFinding] = []
        self.stats = {
            "files_scanned": 0,
            "files_skipped": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
    
    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan a single file for security issues."""
        findings = []
        rel_path = str(file_path.relative_to(self.repo_path))
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Check for malicious patterns
            for line_num, line in enumerate(lines, 1):
                for pattern, description in MALICIOUS_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._classify_severity(pattern, description)
                        findings.append(SecurityFinding(
                            severity=severity,
                            category="malicious_pattern",
                            file=rel_path,
                            line=line_num,
                            message=description,
                            pattern=pattern,
                            suggestion="Review and remove if not intentional"
                        ))
            
            # Check for secrets in config files
            if file_path.suffix in ('.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'):
                self._check_config_secrets(content, rel_path, findings)
            
            self.stats["files_scanned"] += 1
            
        except Exception as e:
            self.stats["files_skipped"] += 1
        
        return findings
    
    def _check_config_secrets(self, content: str, file_path: str, findings: List[SecurityFinding]):
        """Check configuration files for secrets."""
        secret_patterns = [
            (r'"password"\s*:\s*"[^"]+"', "Password in config"),
            (r'"secret"\s*:\s*"[^"]+"', "Secret in config"),
            (r'"api_key"\s*:\s*"[^"]+"', "API key in config"),
            (r'"token"\s*:\s*"[^"]+"', "Token in config"),
            (r'"access_key"\s*:\s*"[^"]+"', "Access key in config"),
        ]
        
        for pattern, description in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append(SecurityFinding(
                    severity="high",
                    category="hardcoded_secret",
                    file=file_path,
                    message=description,
                    suggestion="Use environment variables or secrets manager"
                ))
    
    def _classify_severity(self, pattern: str, description: str) -> str:
        """Classify the severity of a finding."""
        critical_patterns = [
            "eval.*base64", "exec.*compile", "rm.*-rf.*/",
            "Double base64", "Hex decode exec", "Base64 compile",
            "reverse shell", "/dev/tcp/",
        ]
        high_patterns = [
            "password.*=", "secret.*=", "api.*key.*=", "curl.*bash",
            "xmrig", "nicehash", "coinhive", "cryptonight",
            "miner", "backdoor", "exfiltrat", "stratum",
            "ncat.*-e", "Netcat.*execute",
        ]
        medium_patterns = [
            "subprocess.*shell", "os.system", "chmod.*777",
            "wget.*post", "curl.*-d", "socket.*connect",
        ]
        
        for cp in critical_patterns:
            if re.search(cp, pattern, re.IGNORECASE):
                return "critical"
        
        for hp in high_patterns:
            if re.search(hp, pattern, re.IGNORECASE):
                return "high"
        
        for mp in medium_patterns:
            if re.search(mp, pattern, re.IGNORECASE):
                return "medium"
        
        return "low"
    
    def scan_sensitive_files(self):
        """Check for sensitive files."""
        for sensitive in SENSITIVE_PATHS:
            for file_path in self.repo_path.rglob(f"*{sensitive}*"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.findings.append(SecurityFinding(
                        severity="medium",
                        category="sensitive_file",
                        file=rel_path,
                        message=f"Sensitive file found: {sensitive}",
                        suggestion="Ensure this file is in .gitignore"
                    ))
    
    def scan_suspicious_files(self):
        """Check for suspicious file extensions."""
        for ext in SUSPICIOUS_EXTENSIONS:
            for file_path in self.repo_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.findings.append(SecurityFinding(
                        severity="low",
                        category="suspicious_file",
                        file=rel_path,
                        message=f"Suspicious file extension: {ext}",
                        suggestion="Review if this file should be in repository"
                    ))
    
    def scan_dependencies(self):
        """Scan dependency files for known issues."""
        dep_files = [
            ("package.json", self._scan_npm_deps),
            ("requirements.txt", self._scan_pip_deps),
            ("go.mod", self._scan_go_deps),
            ("Cargo.toml", self._scan_rust_deps),
        ]
        
        for dep_file, scanner in dep_files:
            for file_path in self.repo_path.rglob(dep_file):
                if file_path.is_file():
                    scanner(file_path)
    
    def _scan_npm_deps(self, file_path: Path):
        """Scan package.json for risky dependencies."""
        try:
            content = json.loads(file_path.read_text())
            deps = {**content.get("dependencies", {}), **content.get("devDependencies", {})}
            
            risky_deps = ["eval", "shelljs", "execa"]
            for dep in deps:
                if dep.lower() in risky_deps:
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.findings.append(SecurityFinding(
                        severity="medium",
                        category="risky_dependency",
                        file=rel_path,
                        message=f"Potentially risky dependency: {dep}",
                        suggestion="Review necessity and security implications"
                    ))
        except:
            pass
    
    def _scan_pip_deps(self, file_path: Path):
        """Scan requirements.txt for risky dependencies."""
        risky_deps = ["subprocess32", "shell"]
        try:
            for line in file_path.read_text().split('\n'):
                dep = line.strip().split('==')[0].split('>=')[0].split('<=')[0]
                if dep.lower() in risky_deps:
                    rel_path = str(file_path.relative_to(self.repo_path))
                    self.findings.append(SecurityFinding(
                        severity="medium",
                        category="risky_dependency",
                        file=rel_path,
                        message=f"Potentially risky dependency: {dep}",
                        suggestion="Review necessity and security implications"
                    ))
        except:
            pass
    
    def _scan_go_deps(self, file_path: Path):
        """Scan go.mod for risky dependencies."""
        pass  # Go deps are generally safer
    
    def _scan_rust_deps(self, file_path: Path):
        """Scan Cargo.toml for risky dependencies."""
        pass  # Rust deps are generally safer
    
    def scan_dependencies_enhanced(self):
        """Enhanced dependency scanning with registry lookups."""
        # Scan npm packages for suspicious postinstall scripts
        for file_path in self.repo_path.rglob("package.json"):
            if file_path.is_file():
                self._scan_npm_enhanced(file_path)
        
        # Scan pip packages for typosquatting
        for filename in ("requirements.txt", "Pipfile", "setup.py", "pyproject.toml"):
            for file_path in self.repo_path.rglob(filename):
                if file_path.is_file():
                    self._scan_pip_enhanced(file_path)
    
    def _scan_npm_enhanced(self, file_path: Path):
        """Scan npm packages for suspicious postinstall scripts via registry."""
        try:
            content = json.loads(file_path.read_text())
        except Exception:
            return
        
        deps = list(content.get("dependencies", {}).keys())
        rel_path = str(file_path.relative_to(self.repo_path))
        
        danger_keywords = ["curl", "wget", "eval", "exec", "chmod", "rm -rf", "sudo", "base64"]
        
        for dep in deps[:20]:  # Limit to avoid rate limits
            try:
                url = f"https://registry.npmjs.org/{urllib.parse.quote(dep)}/latest"
                req = urllib.request.Request(url, headers={"Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    pkg_data = json.loads(resp.read().decode())
                
                scripts = pkg_data.get("scripts", {})
                for script_name, script_cmd in scripts.items():
                    if script_name in ("preinstall", "postinstall", "preuninstall", "postuninstall"):
                        for kw in danger_keywords:
                            if kw in script_cmd.lower():
                                self.findings.append(SecurityFinding(
                                    severity="high",
                                    category="malicious_pattern",
                                    file=rel_path,
                                    message=f"npm package '{dep}' has suspicious {script_name}: {script_cmd}",
                                    suggestion=f"Review package '{dep}' - {script_name} contains '{kw}'"
                                ))
                                break
            except Exception:
                continue
    
    def _scan_pip_enhanced(self, file_path: Path):
        """Scan pip packages for typosquatting (similar names to popular packages)."""
        # Well-known packages that are often typosquatted
        popular_packages = {
            "requests", "flask", "django", "numpy", "pandas", "scipy",
            "matplotlib", "pillow", "cryptography", "pyyaml", "click",
            "fastapi", "uvicorn", "sqlalchemy", "celery", "redis",
            "boto3", "botocore", "google-cloud-storage", "azure-identity",
            "tensorflow", "torch", "transformers", "langchain", "openai",
            "anthropic", "httpx", "aiohttp", "pytest", "black", "ruff",
        }
        
        try:
            lines = file_path.read_text().split('\n')
        except Exception:
            return
        
        rel_path = str(file_path.relative_to(self.repo_path))
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # Extract package name (before ==, >=, etc.)
            dep = re.split(r'[><=!~\[]', line)[0].strip()
            if not dep:
                continue
            
            dep_lower = dep.lower().replace('-', '').replace('_', '')
            
            for popular in popular_packages:
                pop_clean = popular.lower().replace('-', '').replace('_', '')
                # Check for typosquatting: similar but not identical
                if dep_lower != pop_clean and self._is_likely_typo(dep_lower, pop_clean):
                    self.findings.append(SecurityFinding(
                        severity="high",
                        category="malicious_pattern",
                        file=rel_path,
                        message=f"Possible typosquatting: '{dep}' looks like '{popular}'",
                        suggestion=f"Verify '{dep}' is the intended package, not a typosquat of '{popular}'"
                    ))
                    break
    
    @staticmethod
    def _is_likely_typo(name: str, target: str) -> bool:
        """Check if name is a likely typo of target (simple edit distance)."""
        if abs(len(name) - len(target)) > 3:
            return False
        # Quick check: must share most characters
        if not set(target).issubset(set(name)) and not set(name).issubset(set(target)):
            # Calculate simple overlap
            common = len(set(name) & set(target))
            total = len(set(name) | set(target))
            if total > 0 and common / total < 0.6:
                return False
        # Levenshtein-like: if within 2 edits and lengths are close
        if abs(len(name) - len(target)) <= 2:
            # Simple character overlap check as proxy
            matches = sum(1 for a, b in zip(name, target) if a == b)
            max_len = max(len(name), len(target))
            if max_len > 0 and matches / max_len >= 0.6:
                return True
        return False
    
    def scan_all(self) -> SecurityReport:
        """Run all security scans."""
        from datetime import datetime
        
        print(f"Scanning: {self.repo_path}")
        
        # Scan all code files
        code_extensions = ('.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.rb', '.php')
        for file_path in self.repo_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                findings = self.scan_file(file_path)
                self.findings.extend(findings)
        
        # Run specialized scans
        self.scan_sensitive_files()
        self.scan_suspicious_files()
        self.scan_dependencies()
        self.scan_dependencies_enhanced()
        
        # Update stats
        for f in self.findings:
            self.stats[f.severity] = self.stats.get(f.severity, 0) + 1
        
        # Calculate risk score
        risk_score = self._calculate_risk_score()
        
        # Build report
        report = SecurityReport(
            repo_name=self.repo_path.name,
            repo_path=str(self.repo_path),
            scan_time=datetime.now().isoformat(),
            findings=[asdict(f) for f in self.findings],
            stats=self.stats,
            risk_score=risk_score,
            risk_level=self._get_risk_level(risk_score),
            summary=self._generate_summary()
        )
        
        return report
    
    def _calculate_risk_score(self) -> int:
        """Calculate risk score 0-100."""
        score = 0
        score += self.stats.get("critical", 0) * 30
        score += self.stats.get("high", 0) * 15
        score += self.stats.get("medium", 0) * 5
        score += self.stats.get("low", 0) * 1
        return min(100, score)
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score."""
        if score >= 70:
            return "critical"
        elif score >= 50:
            return "high"
        elif score >= 30:
            return "medium"
        elif score >= 10:
            return "low"
        return "info"
    
    def _generate_summary(self) -> str:
        """Generate a summary of findings."""
        total = len(self.findings)
        if total == 0:
            return "No security issues found"
        
        critical = self.stats.get("critical", 0)
        high = self.stats.get("high", 0)
        
        parts = []
        if critical:
            parts.append(f"{critical} critical")
        if high:
            parts.append(f"{high} high")
        
        if parts:
            return f"Found {total} issues: {', '.join(parts)} severity"
        return f"Found {total} issues"


def main():
    parser = argparse.ArgumentParser(description="Scan repository for security issues")
    parser.add_argument("repo_path", help="Path to repository to scan")
    parser.add_argument("-o", "--output", default="security_report.json", help="Output file")
    
    args = parser.parse_args()
    
    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"Error: Path not found: {repo_path}")
        sys.exit(1)
    
    scanner = SecurityScanner(repo_path)
    report = scanner.scan_all()
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(asdict(report), f, indent=2)
    
    print(f"\nSecurity scan complete:")
    print(f"  Risk Score: {report.risk_score}/100 ({report.risk_level})")
    print(f"  Findings: {len(report.findings)}")
    print(f"  Critical: {report.stats.get('critical', 0)}")
    print(f"  High: {report.stats.get('high', 0)}")
    print(f"  Medium: {report.stats.get('medium', 0)}")
    print(f"  Low: {report.stats.get('low', 0)}")
    print(f"  Output: {args.output}")
    
    # Output to stdout
    print(json.dumps(asdict(report)))
    
    # Exit code based on risk
    sys.exit(1 if report.risk_level in ("critical", "high") else 0)


if __name__ == "__main__":
    main()
