# Security Patterns Catalog

Detailed security patterns checked during pre-clone and deep scanning.

## Table of Contents
1. [Critical Patterns](#critical-patterns)
2. [High Patterns](#high-patterns)
3. [Medium Patterns](#medium-patterns)
4. [Low Patterns](#low-patterns)
5. [Dependency Risks](#dependency-risks)

## Critical Patterns

### Code Injection
- `eval()` with dynamic input
- `exec()` / `compile()` with user data
- `subprocess.call(shell=True)` with variables
- `child_process.exec()` with template literals

### Remote Code Execution
- `os.system()` / `os.popen()` with variables
- `child_process.spawn()` with shell flags
- HTTP requests that execute response bodies

### Data Destruction
- `rm -rf` in loops or with variables
- `DROP TABLE` / `DELETE FROM` without WHERE
- `os.remove()` / `shutil.rmtree()` in loops

### Crypto Mining
- `xmrig` / `stratum+tcp` / `nicehash`
- `minerd` / `cryptonight` / `coinhive`
- `crypto.btc` mining pool connections

### Backdoors
- `/dev/tcp` reverse shells
- `ncat -e` / `nc -e` connections
- `bash -i >& /dev/tcp` patterns
- Python `socket.connect()` with exec

## High Patterns

### Hardcoded Secrets
- API keys in source: `sk-`, `ghp_`, `AKIA`
- Database passwords in config files
- Private keys in repository

### Sensitive Files
- `.env` with secrets
- `.pem` / `.key` / `id_rsa`
- `credentials.json` / `service-account.json`

### Dangerous Permissions
- `chmod 777` on any file
- World-writable directories
- SUID/SGID bits set

### Data Exfiltration
- `requests.post()` with `os.environ`
- `curl -X POST` with file contents
- `wget --post-file` with sensitive paths

## Medium Patterns

### Shell Execution
- `subprocess.Popen()` without `shell=False`
- `os.system()` with string formatting
- Backtick execution in shell scripts

### Risky Dependencies
- npm packages with suspicious postinstall
- PyPI typosquatting (name similarity)
- Go modules from untrusted sources

### Debug Mode
- `DEBUG=True` in production configs
- Verbose logging enabled by default
- Development endpoints exposed

## Low Patterns

### Suspicious Extensions
- `.exe` / `.bat` / `.ps1` in source
- Obfuscated file names
- Hidden files with code

### Large Files
- Files >500 lines (potential god files)
- Binary blobs in source
- Minified code without source

## Dependency Risks

### npm
- `preinstall` / `postinstall` scripts with curl/wget/eval
- Packages mimicking popular names (typosquatting)
- Dependencies from unknown publishers

### PyPI
- Packages with similar names to popular ones (e.g., `requessts` vs `requests`)
- Packages with shell commands in setup.py
- Recently created packages mimicking established ones

### Go/Rust
- Dependencies from forks, not upstream
- Dependencies with unsafe code blocks
- Dependencies with network access in build scripts
