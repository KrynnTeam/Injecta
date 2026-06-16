"""
Injecta — Automated report generation (HTML & JSON)
"""
import json
import os
import time
from typing import Any, Dict, List, Optional


class ReportGenerator:
    def __init__(self, config, logger):
        self.config = config
        self.log = logger
        self.output_dir = config.output_dir or "reports"
        self.ts = time.strftime("%Y%m%d_%H%M%S")

    def generate_json(self, data: Dict[str, Any], filename: str = "") -> str:
        if not filename:
            filename = f"injecta_report_{self.ts}.json"
        path = os.path.join(self.output_dir, filename)
        os.makedirs(self.output_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        self.log.ok(f"JSON report: {path}")
        return path

    def generate_html(self, data: Dict[str, Any], filename: str = "") -> str:
        if not filename:
            filename = f"injecta_report_{self.ts}.html"
        path = os.path.join(self.output_dir, filename)
        os.makedirs(self.output_dir, exist_ok=True)

        html = self._build_html(data)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        self.log.ok(f"HTML report: {path}")
        return path

    def _build_html(self, data: Dict[str, Any]) -> str:
        target = data.get("target", "Unknown")
        dbms = data.get("dbms", "Unknown")
        vuln_count = len(data.get("params", []))

        params_rows = ""
        for p in data.get("params", []):
            param = p.get("param", "?")
            tech = p.get("technique", "?")
            conf = p.get("confidence", 0)
            conf_pct = f"{conf * 100:.0f}%"
            sev = "critical" if conf >= 0.9 else "high" if conf >= 0.7 else "medium"
            params_rows += f"""
            <tr>
                <td>{param}</td>
                <td><span class="sev {sev}">{sev}</span></td>
                <td>{tech}</td>
                <td>{conf_pct}</td>
            </tr>"""

        waf_list = data.get("waf", [])
        waf_html = ", ".join(waf_list) if waf_list else "None detected"

        privesc = data.get("privesc", {})
        privesc_html = ""
        if privesc:
            privesc_html = f"""
            <div class="section">
                <h2>Privilege Escalation</h2>
                <table>
                    <tr><th>User</th><td>{privesc.get('user', 'Unknown')}</td></tr>
                    <tr><th>Admin</th><td>{'Yes' if privesc.get('is_admin') else 'No'}</td></tr>
                    <tr><th>Privileges</th><td>{', '.join(privesc.get('privileges', [])) or 'None'}</td></tr>
                </table>
            </div>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Injecta Report - {target}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',-apple-system,sans-serif;background:#1a0808;color:#faf5f5;padding:40px}}
.container{{max-width:960px;margin:0 auto}}
h1{{font-size:28px;font-weight:800;margin-bottom:4px;background:linear-gradient(135deg,#fff,#c41e3a,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.meta{{color:rgba(250,245,245,0.5);font-size:13px;margin-bottom:32px}}
.section{{background:rgba(45,15,15,0.6);border:1px solid rgba(139,0,0,0.15);border-radius:20px;padding:24px;margin-bottom:20px}}
.section h2{{font-size:16px;font-weight:600;margin-bottom:16px;color:#c41e3a}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th{{text-align:left;padding:10px 12px;color:rgba(250,245,245,0.5);font-size:11px;text-transform:uppercase;letter-spacing:0.3px;border-bottom:1px solid rgba(139,0,0,0.1)}}
td{{padding:10px 12px;border-bottom:1px solid rgba(139,0,0,0.06)}}
.sev{{padding:2px 10px;border-radius:6px;font-size:10px;font-weight:600;text-transform:uppercase}}
.sev.critical{{background:rgba(248,113,113,0.12);color:#f87171}}
.sev.high{{background:rgba(251,146,60,0.12);color:#fb923c}}
.sev.medium{{background:rgba(251,191,36,0.12);color:#fbbf24}}
.tag{{display:inline-block;padding:2px 10px;border-radius:6px;background:rgba(139,0,0,0.1);border:1px solid rgba(139,0,0,0.15);font-size:11px;margin:2px}}
.summary-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}}
.summary-card{{background:rgba(45,15,15,0.4);border:1px solid rgba(139,0,0,0.1);border-radius:12px;padding:16px;text-align:center}}
.summary-card .val{{font-size:24px;font-weight:800}}
.summary-card .lbl{{font-size:11px;color:rgba(250,245,245,0.5);margin-top:2px}}
.footer{{text-align:center;font-size:11px;color:rgba(250,245,245,0.3);margin-top:32px}}
</style>
</head>
<body>
<div class="container">
    <h1>Injecta Intelligence Report</h1>
    <div class="meta">Target: {target} &middot; {self.ts} &middot; Made by Kael / Krynn Team</div>

    <div class="summary-grid">
        <div class="summary-card"><div class="val" style="color:#c41e3a">{vuln_count}</div><div class="lbl">Vulnerabilities</div></div>
        <div class="summary-card"><div class="val" style="color:#7c3aed">{dbms}</div><div class="lbl">Database</div></div>
        <div class="summary-card"><div class="val" style="color:#ec4899">{len(waf_list)}</div><div class="lbl">WAFs Detected</div></div>
    </div>

    <div class="section">
        <h2>Target</h2>
        <table>
            <tr><th>URL</th><td>{target}</td></tr>
            <tr><th>DBMS</th><td>{dbms}</td></tr>
            <tr><th>WAF</th><td>{waf_html}</td></tr>
            <tr><th>Techniques</th><td>{', '.join(p.get('technique', '?') for p in data.get('params', [])) or 'None'}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Vulnerable Parameters ({vuln_count})</h2>
        <table>
            <thead><tr><th>Parameter</th><th>Severity</th><th>Technique</th><th>Confidence</th></tr></thead>
            <tbody>{params_rows if params_rows else '<tr><td colspan="4" style="text-align:center;color:rgba(250,245,245,0.3)">No vulnerable parameters found</td></tr>'}</tbody>
        </table>
    </div>

    {privesc_html}

    <div class="section">
        <h2>Raw Data</h2>
        <pre style="font-size:11px;color:rgba(250,245,245,0.5);overflow-x:auto;max-height:300px">{json.dumps(data, indent=2, default=str)}</pre>
    </div>

    <div class="footer">Generated by Injecta &middot; Kael / Krynn Team</div>
</div>
</body>
</html>"""

    def generate_all(self, data: Dict[str, Any]) -> Dict[str, str]:
        return {
            "json": self.generate_json(data),
            "html": self.generate_html(data),
        }
