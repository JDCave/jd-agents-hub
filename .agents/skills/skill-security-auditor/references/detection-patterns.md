# Detection Patterns Reference

Complete catalogue of what `skill_security_auditor.py` scans for. The
severity-to-verdict mapping: any CRITICAL → FAIL; any HIGH → WARN; INFO-only → PASS.

## 1. Code Execution Risks (Python/Bash/JS Scripts)

Scans all `.py`, `.sh`, `.bash`, `.js`, `.ts` files for:

| Category | Patterns Detected | Severity |
|----------|-------------------|----------|
| **Command injection** | `os.system()`, `os.popen()`, `subprocess.call(shell=True)`, backtick execution | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Code execution** | `eval()`, `exec()`, `compile()`, `__import__()` | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Obfuscation** | base64-encoded payloads, `codecs.decode`, hex-encoded strings, `chr()` chains | CRITICAL |
| **Network exfiltration** | `requests.post()`, `urllib.request`, `socket.connect()`, `httpx`, `aiohttp` | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Credential harvesting** | reads from `~/.ssh`, `~/.aws`, `~/.config`, env var extraction patterns | CRITICAL |
| **File system abuse** | writes outside skill dir, `/etc/`, `~/.bashrc`, `~/.profile`, symlink creation | HIGH |
| **Privilege escalation** | `sudo`, `chmod 777`, `setuid`, cron manipulation | CRITICAL |
| **Unsafe deserialization** | `pickle.loads()`, `yaml.load()` (without SafeLoader), `marshal.loads()` | HIGH | <!-- noqa: SEC-AUDITOR -->
| **Subprocess (safe)** | `subprocess.run()` with list args, no shell | INFO |

## 2. Prompt Injection in SKILL.md and Reference Markdown

| Pattern | Example | Severity |
|---------|---------|----------|
| **System prompt override** | "Ignore previous instructions", "You are now..." | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Role hijacking** | "Act as root", "Pretend you have no restrictions" | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Safety bypass** | "Skip safety checks", "Disable content filtering" | CRITICAL | <!-- noqa: SEC-AUDITOR -->
| **Hidden instructions** | Zero-width characters, HTML comments with directives | HIGH |
| **Excessive permissions** | "Run any command", "Full filesystem access" | HIGH |
| **Data extraction** | "Send contents of", "Upload file to", "POST to" | CRITICAL | <!-- noqa: SEC-AUDITOR -->

## 3. Dependency Supply Chain

For skills with `requirements.txt`, `package.json`, or inline `pip install`:

| Check | What It Does | Severity |
|-------|-------------|----------|
| **Known vulnerabilities** | Cross-reference with PyPI/npm advisory databases | CRITICAL |
| **Typosquatting** | Flag packages similar to popular ones (e.g., `reqeusts`) | HIGH |
| **Unpinned versions** | Flag `requests>=2.0` vs `requests==2.31.0` | INFO |
| **Install commands in code** | `pip install` or `npm install` inside scripts | HIGH |
| **Suspicious packages** | Low download count, recent creation, single maintainer | INFO |

## 4. File System & Structure

| Check | What It Does | Severity |
|-------|-------------|----------|
| **Boundary violation** | Scripts referencing paths outside skill directory | HIGH |
| **Hidden files** | `.env`, dotfiles that shouldn't be in a skill | HIGH |
| **Binary files** | Unexpected executables, `.so`, `.dll`, `.exe` | CRITICAL |
| **Large files** | Files >1MB that could hide payloads | INFO |
| **Symlinks** | Symbolic links pointing outside skill directory | CRITICAL |

## Suppression

A line ending in `# noqa: SEC-AUDITOR` (or containing `auditor:ignore-line`)
is skipped by the scanner. Legitimate uses: security tooling that contains the
dangerous-pattern strings it detects, and test fixtures exercising those
detectors. Never use it to silence a real finding.
