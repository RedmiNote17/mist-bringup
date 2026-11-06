#!/usr/bin/env python3
"""Small bounded range probes; never retrieve an entire firmware archive."""
import concurrent.futures
import json
import pathlib
import subprocess
import sys
from urllib.parse import urlparse

RANGE_END = 8 * 1024 * 1024 - 1
MAX_BYTES = 9 * 1024 * 1024
ALLOWED = {"bigota.d.miui.com", "hugeota.d.miui.com"}

def probe(candidate):
    u = candidate["url"]
    if urlparse(u).scheme != "https" or urlparse(u).hostname not in ALLOWED:
        return {"label": candidate["label"], "error": "host is not approved"}
    fmt = "HTTP=%{http_code} bytes=%{size_download} speed_Bps=%{speed_download} seconds=%{time_total} final=%{url_effective}"
    cmd = ["curl", "-sS", "-L", "--proto", "=https", "--proto-redir", "=https",
           "--connect-timeout", "8", "--max-time", "40", "--max-filesize", str(MAX_BYTES),
           "--range", f"0-{RANGE_END}", "--output", "/dev/null",
           "--write-out", fmt, u]
    try:
        r = subprocess.run(cmd, text=True, capture_output=True, timeout=45)
        return {"label": candidate["label"], "curl_exit_code": r.returncode,
                "metrics": r.stdout.strip(), "error": r.stderr.strip()[-400:]}
    except Exception as e:
        return {"label": candidate["label"], "error": str(e)}

def main():
    candidates = json.loads(pathlib.Path(sys.argv[1]).read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(probe, candidates))
    report = pathlib.Path(sys.argv[2])
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2)+"\n")
    lines=["# Xiaomi CDN partial-transfer probe", "",
           "Tests fetch at most 8 MiB per host. Status HTTP 206 and a bytes count near 8 MiB indicates valid range support.",
           "Results describe this GitHub runner only; source performance varies by time and location.",
           "",
           "| Candidate | Result |", "| --- | --- |"]
    for item in results:
        result=(item.get("metrics") or item.get("error", "failed")).replace("|", "/")
        lines.append(f"| {item['label']} | {result} |")
        print(item["label"], item.get("curl_exit_code", "-"), result, flush=True)
    summary="\n".join(lines)+"\n"
    (report.parent / "SUMMARY.md").write_text(summary)
    step=pathlib.os.environ.get("GITHUB_STEP_SUMMARY")
    if step:
        with open(step,"a") as f: f.write(summary)

if __name__ == "__main__":
    main()
