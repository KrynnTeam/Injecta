<div align="center">

<img src="https://readme-typing-svg.herokuapp.com/?font=Fira+Code&size=24&pause=1000&color=E94560&center=true&vCenter=true&width=700&lines=Injecta+%7C+SQL+Injection+Automation;Detection+%E2%86%92+Extraction+%E2%86%92+Exfiltration;Practical+tooling+for+real+tests" alt="Typing SVG" />

</div>

### SQL Injection Automation Framework — Detection → Extraction → Exfiltration

Zero web dependencies · 6 DBMS backends · 5 injection techniques · 19 WAF tamper scripts · Plugin system

---

## Overview

Injecta is a lightweight SQL injection automation framework designed for real penetration tests. It focuses on detection, enumeration, extraction, and reporting while keeping dependencies minimal.

- Practical execution over flashy UI
- Strong focus on WAF bypass and evasive payloads
- Built to work with multiple database engines

---

## Quick start

```bash
git clone https://github.com/KrynnTeam/Injecta.git
cd Injecta
pip install -r requirements.txt
python run.py -u "http://testphp.vulnweb.com/artists.php?artist=1"
```

---

## Launch modes

| Mode | Description | Example |
|---|---|---|
| CLI | Direct scan from the command line | `python run.py -u URL` |
| Dashboard | Browser-based UI and REST API | `python run.py --web` |
| Interactive | REPL mode for manual control | `python run.py --interactive` |

---

## CLI reference

<details>
<summary><strong>🎯 Target & request</strong></summary>

| Flag | Description | Default |
|---|---|---|
| `-u, --url` | Target URL | — |
| `-m, --method` | HTTP method (`GET` / `POST`) | `GET` |
| `-d, --data` | POST body data | — |
| `--cookie` | HTTP cookies | — |
| `-H, --header` | Custom request headers | — |
| `--proxy` | Proxy URL | — |
| `--tor` | Use Tor proxy | `false` |
| `--threads` | Number of threads | `1` |
| `--delay` | Delay between requests | `0` |
| `--timeout` | Request timeout in seconds | `10` |
| `--retries` | Retry count | `3` |
| `--random-agent` | Random User-Agent per request | `true` |

</details>

<details>
<summary><strong>💉 Injection control</strong></summary>

| Flag | Description | Default |
|---|---|---|
| `--dbms` | Force DBMS | `auto` |
| `--technique` | Techniques: boolean, error, union, time, stacked | `auto` |
| `--level` | Scan intensity | `1` |
| `--risk` | Payload risk | `1` |

</details>

<details>
<summary><strong>📊 Enumeration</strong></summary>

| Flag | Description |
|---|---|
| `--dbs` | Enumerate databases |
| `--tables` | Enumerate tables |
| `--columns` | Enumerate columns |
| `--dump` | Dump data |
| `-D, --db` | Target database |
| `-T, --table` | Target table |
| `-C, --column` | Target column(s) |
| `--search` | Search columns or tables |
| `--query` | Run raw SQL query |

</details>

<details>
<summary><strong>📁 File & OS operations</strong></summary>

| Flag | Description |
|---|---|
| `--file-read <path>` | Read file from target DB server |
| `--file-write <path>` | Write file on target DB server |
| `--file-write-content <str>` | Data to write |
| `--file-write-local <path>` | Local file upload path |
| `--os-cmd <cmd>` | Execute OS command via DB shell |

</details>

<details>
<summary><strong>🧪 Advanced scans</strong></summary>

| Flag | Description |
|---|---|
| `--nosql` | NoSQL injection support |
| `--graphql` | GraphQL scanning and injection |
| `--privesc` | Privilege escalation checks |
| `--oob-host <host>` | OOB exfiltration target |
| `--cms` | CMS fingerprinting |
| `--second-order` | Second-order SQL injection |
| `--ws` | WebSocket scanning |
| `--plugins` | Load custom plugin modules |

</details>

<details>
<summary><strong>📤 Output & mode</strong></summary>

| Flag | Description | Default |
|---|---|---|
| `--report` | Generate HTML and JSON report | `false` |
| `--web` | Launch web dashboard | `false` |
| `--api` | Start REST API mode | `false` |
| `--interactive` | Start interactive REPL | `false` |
| `--web-port` | Dashboard/API port | `8080` |
| `-v` | Verbosity level | `0` |
| `-o, --output-dir` | Output directory | `./reports` |
| `--batch` | Non-interactive mode | `false` |
| `--flush` | Clear cache/results | `false` |
| `--no-color` | Disable color output | `false` |

</details>

---

## Features

- **Injection detection:** Boolean, time-based, error-based, UNION, stacked.
- **Blind optimizer:** Binary search and bitwise extraction for fewer requests.
- **CMS fingerprinting:** WordPress, Joomla, Drupal, Magento, phpMyAdmin.
- **Second-order support:** Stored payload and delayed execution paths.
- **WebSocket scanning:** Frame injection and endpoint discovery.
- **Plugin system:** Auto-discovered plugins with lifecycle hooks.
- **File I/O:** Read/write via `LOAD_FILE`, `COPY`, `pg_read_file`, `UTL_FILE`.
- **OS command execution:** `xp_cmdshell`, UDF injection, `DBMS_SCHEDULER`.
- **OOB exfiltration:** DNS, HTTP, SMB channels.
- **WAF evasion:** Multiple tamper scripts, auto-chains, and signature detection.
- **Reports:** HTML summary and JSON export.
- **Docker-ready:** `docker compose up -d` with dashboard on port `8080`.

---

## WAF detection & evasion

| WAF | Signature | Tamper chain |
|---|---|---|
| Cloudflare | `cf-ray`, `__cfduid` | `space2comment`, `randomcase` |
| ModSecurity | `x-mod-security` | `hexencode`, `commentkeywords` |
| AWS WAF | `x-amzn-requestid` | `randomcase`, `charencode` |
| Akamai | `x-akamai-transformed` | `eq2like`, `nested_comment` |
| F5 BIG-IP ASM | `x-asm-version` | `space2comment`, `unicode_urlencode` |
| Sucuri | `x-sucuri-id` | `hex2dec`, `comment_between` |
| Barracuda | `x-barracuda` | `scientific`, `nullbyte` |
| Wordfence | body pattern match | `double_urlencode`, `greatest` |
| Generic WAF | generic patterns | `greatest`, `least` |

---

## DBMS support

- MySQL
- PostgreSQL
- MSSQL
- Oracle
- SQLite
- Auto-detect

---

## Plugin system

Plugins are Python files in `injecta/plugins/` and extend `BasePlugin`.

```python
from injecta.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    name = "my_plugin"
    description = "Custom payload modifier"
    version = "1.0"
    author = "you"

    def on_scan_start(self, url):
        print(f"Scanning {url} with my plugin")

    def on_payload(self, payload, dbms):
        return payload.upper()
```

**Plugin hooks:**

| Hook | When it runs | Can modify |
|---|---|---|
| `initialize(engine)` | On startup | — |
| `on_scan_start(url)` | Before scan | — |
| `on_payload(payload, dbms)` | Before request | ✅ payload |
| `on_result(result)` | After detection | ✅ result |
| `on_scan_complete(url, results)` | After scan | — |

---

## Project structure

```text
injecta/
├── run.py
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/
└── injecta/
    ├── core/
    ├── enum/
    ├── techniques/
    ├── payloads/
    ├── plugins/
    └── utils/
```

---

## Requirements

- Python 3.10+
- requests
- urllib3
- colorama

---
