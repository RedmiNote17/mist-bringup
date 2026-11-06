#!/usr/bin/env python3
"""Pick the fastest *working* official Xiaomi mirror using bounded HTTP ranges.

Every request is limited to 8 MiB. No firmware is downloaded here.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from urllib.parse import urlparse, urlunparse

from firmware import validate_manifest

HOSTS = (
    "cdnorg.d.miui.com",
    "bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com",
    "bn.d.miui.com",
    "ultimateota.d.miui.com",
)
SAMPLE_BYTES = 8 * 1024 * 1024


def test_host(base_url, host):
    p = urlparse(base_url)
    url = urlunparse(p._replace(netloc=host))
    fmt = "%{http_code}|%{size_download}|%{speed_download}|%{url_effective}"
    args = [
        "curl", "-sS", "-L", "--proto", "=https", "--proto-redir", "=https",
        "--connect-timeout", "5", "--max-time", "16",
        "--max-filesize", str(SAMPLE_BYTES + 1024),
        "--range", f"0-{SAMPLE_BYTES - 1}", "-o", "/dev/null",
        "-w", fmt, url,
    ]
    try:
        r = subprocess.run(args, text=True, capture_output=True, timeout=19)
        code, size, speed, effective = r.stdout.strip().split("|", 3)
        actual = urlparse(effective)
        valid = (
            r.returncode == 0 and code == "206"
            and int(float(size)) == SAMPLE_BYTES
            and actual.scheme == "https"
            and actual.hostname in HOSTS
            and actual.path == p.path
        )
        return {"host": host, "url": url, "status": int(code),
                "bytes": int(float(size)), "speed_Bps": round(float(speed)),
                "valid": valid, "exit_code": r.returncode}
    except Exception as e:
        return {"host": host, "url": url, "valid": False, "error": str(e)}


def choose(m, measurements):
    valid = sorted((r for r in measurements if r["valid"]),
                   key=lambda r: r["speed_Bps"], reverse=True)
    if valid:
        ordered = [r["url"] for r in valid]
    else:
        # Last known good host from successful full-file MD5 validation.
        ordered = [m["url"], *m.get("fallback_urls", [])]
    new = dict(m)
    new["url"], *new["fallback_urls"] = ordered
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    manifest = json.loads(args.manifest.read_text())
    validate_manifest(manifest)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda h: test_host(manifest["url"], h), HOSTS))
    new = choose(manifest, results)
    validate_manifest(new)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.report.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(new, indent=2) + "\n")
    (args.report / "mirror-benchmark.json").write_text(json.dumps(results, indent=2) + "\n")
    lines = ["# Short mirror benchmark", "", "| Host | MiB/s | Valid range |",
             "| --- | ---: | --- |"]
    for result in results:
        speed = result.get("speed_Bps", 0) / 1024**2
        lines.append(f"| {result['host']} | {speed:.2f} | {result['valid']} |")
        print(result["host"], "MiB/s", round(speed, 2), "valid", result["valid"], flush=True)
    lines += ["", f"Selected: **{urlparse(new['url']).hostname}**",
              "Small sample speeds do not guarantee sustained performance.",
              "Full archive must pass the pinned MD5 before analysis."]
    (args.report / "MIRRORS.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
