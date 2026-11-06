#!/usr/bin/env python3
"""Reconcile unresolved proprietary-file paths using the cached stock EROFS partitions.

Read-only; never downloads stock firmware or copies proprietary binary contents.
"""
import argparse
import json
import os
from pathlib import Path

from analyze_stock import mounted


def source_path(line):
    text = line.strip()
    if not text or text.startswith("#"):
        return None
    path = text.removeprefix("-").split(";")[0].split(":")[0]
    p = Path(path)
    if p.is_absolute() or ".." in p.parts or len(p.parts) < 2:
        raise ValueError("Unsafe proprietary reference path")
    return path


def inspect(root, path, part):
    paths = [root / path]
    if part == "system":
        paths.append(root / "system" / path)
    for candidate in paths:
        if not os.path.lexists(candidate):
            continue
        prefix = candidate.relative_to(root).as_posix()
        if candidate.is_symlink():
            return {"status": "symlink", "image_path": prefix,
                    "link_target": os.readlink(candidate)}
        if candidate.is_file():
            return {"status": "regular", "image_path": prefix}
        if candidate.is_dir():
            return {"status": "directory", "image_path": prefix}
        return {"status": "special", "image_path": prefix}
    return {"status": "absent_from_mounted_image"}


def audit(cache, source_file, out):
    cacheinfo = json.loads((cache / "preparation.json").read_text())
    rows = []
    for line in source_file.read_text().splitlines():
        src = source_path(line)
        if src:
            rows.append({"source": src, "reference_line": line})
    bypart = {}
    for r in rows:
        part, rel = r["source"].split("/", 1)
        bypart.setdefault(part, []).append((r, rel))
    for part, pending in sorted(bypart.items()):
        image = cache / "partitions" / (part + "_a.img")
        if not image.is_file():
            for row, _ in pending:
                row["status"] = "missing_partition_image"
            continue
        with mounted(image, cache / "audit_mount" / part) as root:
            for row, path in pending:
                row.update(inspect(root, path, part))
    out.mkdir(parents=True, exist_ok=True)
    (out / "stock-link-audit.json").write_text(json.dumps({
        "version": cacheinfo["version"], "firmware_md5": cacheinfo["firmware_md5"],
        "entries": rows,
    }, indent=2) + "\n")
    counts = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    summary = [
        "# mist unresolved proprietary-file symlink audit", "",
        "Source: " + cacheinfo["version"],
        "MD5: " + cacheinfo["firmware_md5"],
        "All analysis used the existing GitHub Actions cache, without firmware download.",
        "", "| Result | Count |", "| --- | ---: |",
    ]
    for key in sorted(counts):
        summary.append("| " + key + " | " + str(counts[key]) + " |")
    summary += ["", "A source-path hit is not proof of ABI or runtime compatibility.",
                "No binary firmware files were uploaded.", ""]
    (out / "SUMMARY.md").write_text("\n".join(summary))
    for row in rows:
        print(row["status"], row["source"], row.get("link_target", ""), flush=True)
    print("Symlink audit complete:", counts, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    audit(args.cache, args.reference, args.out)
