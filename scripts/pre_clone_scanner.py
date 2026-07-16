#!/usr/bin/env python3
"""Pre-Clone Scanner - Check repo safety before downloading."""

import json
import sys
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone
from typing import Optional

class PreCloneScanner:
    """Check if a GitHub repo is safe to clone before downloading."""
    
    GITHUB_API = "https://api.github.com"
    
    # Red flag keywords in READMEs/descriptions
    RED_FLAG_KEYWORDS = [
        "crypto miner", "xmrig", "nicehash", "minerd", "stratum+tcp",
        "bitcoin miner", "monero", "coinhive", "cryptonight",
        "reverse shell", "bind shell", "backdoor", "exploit",
        "keylogger", "ransomware", "trojan", "rootkit",
        "steal", "exfiltrate", "harvest credentials",
    ]
    
    # Suspicious package patterns (typosquatting)
    SUSPICIOUS_PATTERNS = [
        r"^[a-z]+-[a-z]+-[a-z]+$",  # too many hyphens
        r"^(test|temp|tmp|debug|dev)-",  # test packages
    ]
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
    
    def _github_get(self, endpoint: str) -> dict:
        """Make a GET request to GitHub API."""
        url = f"{self.GITHUB_API}{endpoint}"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": str(e), "status": e.code}
        except Exception as e:
            return {"error": str(e)}
    
    def _fetch_raw(self, url: str) -> Optional[str]:
        """Fetch raw content from URL."""
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception:
            return None
    
    def check_repo_health(self, owner: str, repo: str) -> dict:
        """Check repo health metrics."""
        data = self._github_get(f"/repos/{owner}/{repo}")
        if "error" in data:
            return {"error": data["error"], "healthy": False}
        
        # Calculate age in days
        created_at = data.get("created_at", "")
        updated_at = data.get("updated_at", "")
        
        age_days = 0
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created).days
            except Exception:
                pass
        
        # Days since last update
        stale_days = 0
        if updated_at:
            try:
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                stale_days = (datetime.now(timezone.utc) - updated).days
            except Exception:
                pass
        
        return {
            "name": data.get("full_name", f"{owner}/{repo}"),
            "description": data.get("description", ""),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "language": data.get("language", ""),
            "license": data.get("license", {}).get("spdx_id", "") if data.get("license") else "",
            "created_at": created_at,
            "updated_at": updated_at,
            "age_days": age_days,
            "stale_days": stale_days,
            "has_wiki": data.get("has_wiki", False),
            "has_pages": data.get("has_pages", False),
            "default_branch": data.get("default_branch", "main"),
            "topics": data.get("topics", []),
            "archived": data.get("archived", False),
            "disabled": data.get("disabled", False),
        }
    
    def check_maintainer(self, owner: str) -> dict:
        """Check maintainer account health."""
        data = self._github_get(f"/users/{owner}")
        if "error" in data:
            return {"error": data["error"]}
        
        created_at = data.get("created_at", "")
        age_days = 0
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - created).days
            except Exception:
                pass
        
        return {
            "login": data.get("login", ""),
            "name": data.get("name", ""),
            "bio": data.get("bio", ""),
            "public_repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "created_at": created_at,
            "account_age_days": age_days,
            "avatar_url": data.get("avatar_url", ""),
        }
    
    def scan_readme_for_red_flags(self, owner: str, repo: str) -> dict:
        """Scan README for red flag keywords."""
        # Try common README filenames
        for filename in ["README.md", "README.rst", "README.txt", "README"]:
            content = self._fetch_raw(
                f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{filename}"
            )
            if content:
                break
        else:
            return {"found": False, "flags": [], "note": "No README found"}
        
        content_lower = content.lower()
        flags = []
        for keyword in self.RED_FLAG_KEYWORDS:
            if keyword.lower() in content_lower:
                # Find the context around the keyword
                idx = content_lower.index(keyword.lower())
                start = max(0, idx - 50)
                end = min(len(content), idx + len(keyword) + 50)
                context = content[start:end].strip()
                flags.append({"keyword": keyword, "context": context})
        
        return {
            "found": len(flags) > 0,
            "flags": flags,
            "readme_length": len(content),
        }
    
    def check_postinstall_scripts(self, owner: str, repo: str) -> dict:
        """Check for suspicious postinstall scripts in package.json."""
        content = self._fetch_raw(
            f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/package.json"
        )
        if not content:
            return {"found": False, "note": "No package.json found"}
        
        try:
            pkg = json.loads(content)
        except json.JSONDecodeError:
            return {"found": False, "note": "Invalid package.json"}
        
        scripts = pkg.get("scripts", {})
        suspicious = {}
        danger_keywords = ["curl", "wget", "eval", "exec", "chmod", "rm -rf", "sudo", "base64"]
        
        for script_name, script_cmd in scripts.items():
            if script_name in ["preinstall", "postinstall", "preuninstall", "postuninstall"]:
                for kw in danger_keywords:
                    if kw in script_cmd.lower():
                        suspicious[script_name] = {"command": script_cmd, "reason": f"Contains '{kw}'"}
                        break
        
        # Check for typosquatting indicators
        name = pkg.get("name", "")
        suspicious_name = False
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.match(pattern, name):
                suspicious_name = True
                break
        
        return {
            "found": len(suspicious) > 0 or suspicious_name,
            "suspicious_scripts": suspicious,
            "suspicious_name": suspicious_name,
            "package_name": name,
        }
    
    def calculate_trust_score(self, health: dict, maintainer: dict, readme: dict, scripts: dict) -> dict:
        """Calculate a trust score 0-100."""
        score = 50  # Start at neutral
        
        # Health factors
        if not health.get("error"):
            stars = health.get("stars", 0)
            if stars >= 1000:
                score += 20
            elif stars >= 100:
                score += 10
            elif stars >= 10:
                score += 5
            else:
                score -= 10
            
            age_days = health.get("age_days", 0)
            if age_days < 7:
                score -= 20  # Very new repo
            elif age_days < 30:
                score -= 10
            elif age_days > 365:
                score += 10
            
            if health.get("archived"):
                score -= 15
            if health.get("license"):
                score += 5
        
        # Maintainer factors
        if not maintainer.get("error"):
            account_age = maintainer.get("account_age_days", 0)
            if account_age < 30:
                score -= 15
            elif account_age > 365:
                score += 10
            
            repos = maintainer.get("public_repos", 0)
            if repos >= 10:
                score += 5
            elif repos < 2:
                score -= 5
        
        # README red flags
        if readme.get("found"):
            score -= 25 * len(readme.get("flags", []))
        
        # Script red flags
        if scripts.get("found"):
            score -= 20
        
        # Clamp to 0-100
        score = max(0, min(100, score))
        
        # Determine level
        if score >= 80:
            level = "safe"
        elif score >= 60:
            level = "caution"
        elif score >= 40:
            level = "risky"
        else:
            level = "dangerous"
        
        return {"score": score, "level": level}
    
    def should_clone(self, repo_url: str) -> dict:
        """Full pre-clone check. Returns decision + reason."""
        # Parse GitHub URL
        match = re.search(r"github\.com/([^/]+)/([^/?#]+)", repo_url)
        if not match:
            return {
                "should_clone": False,
                "reason": "Not a valid GitHub URL",
                "trust_score": {"score": 0, "level": "unknown"},
            }
        
        owner, repo = match.groups()
        
        # Run all checks
        health = self.check_repo_health(owner, repo)
        maintainer = self.check_maintainer(owner)
        readme = self.scan_readme_for_red_flags(owner, repo)
        scripts = self.check_postinstall_scripts(owner, repo)
        
        # Calculate trust score
        trust = self.calculate_trust_score(health, maintainer, readme, scripts)
        
        # Decision
        should = trust["level"] in ["safe", "caution"]
        reasons = []
        
        if readme.get("found"):
            reasons.append(f"README contains red flags: {[f['keyword'] for f in readme.get('flags', [])]}")
        if scripts.get("found"):
            reasons.append(f"Suspicious package scripts: {list(scripts.get('suspicious_scripts', {}).keys())}")
        if health.get("age_days", 999) < 7:
            reasons.append("Repo is less than 7 days old")
        if maintainer.get("account_age_days", 999) < 30:
            reasons.append("Maintainer account is less than 30 days old")
        if health.get("archived"):
            reasons.append("Repo is archived")
        
        return {
            "repo": f"{owner}/{repo}",
            "should_clone": should,
            "trust_score": trust,
            "health": health,
            "maintainer": maintainer,
            "readme_scan": readme,
            "script_scan": scripts,
            "reasons": reasons,
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-clone safety scanner for GitHub repos")
    parser.add_argument("url", help="GitHub repo URL to check")
    parser.add_argument("-o", "--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    scanner = PreCloneScanner()
    result = scanner.should_clone(args.url)
    
    output = json.dumps(result, indent=2, default=str)
    
    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w") as f:
            f.write(output)
        print(f"[OK] Results written to {args.output}")
    else:
        print(output)
    
    # Exit code based on decision
    sys.exit(0 if result["should_clone"] else 1)


if __name__ == "__main__":
    main()
