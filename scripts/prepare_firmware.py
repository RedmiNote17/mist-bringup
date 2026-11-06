#!/usr/bin/env python3
"""Download once and keep selected boot/EROFS partition images in Actions cache."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from firmware import download, validate_manifest
from inspect_partitions import extract_targets, fs_info

EXPECTED = {"odm_a", "product_a", "system_a", "system_dlkm_a",
            "system_ext_a", "vendor_a", "vendor_dlkm_a", "mi_ext_a"}


def prepare(manifest_path, work, lucky):
    m = json.loads(manifest_path.read_text())
    validate_manifest(m)
    work.mkdir(parents=True, exist_ok=True)
    archive = work / m["filename"]
    try:
        integrity = download(m, archive)
        selected = extract_targets(archive, work / "selected")
        archive.unlink(missing_ok=True)
        super_image = selected["super.img"]
        partitions = work / "partitions"
        subprocess.run([str(lucky), "-v", "-l", str(super_image)], check=True)
        subprocess.run([str(lucky), "-o", str(partitions), str(super_image)], check=True)
        super_image.unlink(missing_ok=True)  # Avoid caching the extra 6.5GB sparse file.
        details = [fs_info(p) for p in sorted(partitions.glob("*.img"))]
        found = {p["name"].removesuffix(".img") for p in details}
        if not EXPECTED.issubset(found):
            raise ValueError(f"Missing logical partitions: {sorted(EXPECTED - found)}")
        if not all(x["filesystem"] == "erofs" for x in details):
            raise ValueError("Unexpected filesystem format")
        (work / "preparation.json").write_text(json.dumps({
            "version": m["version"], "firmware_md5": integrity["md5"],
            "firmware_sha256": integrity["sha256"],
            "partitions": details,
        }, indent=2) + "\n")
        print("Firmware prepared and validated; partition images ready for cache", flush=True)
    finally:
        archive.unlink(missing_ok=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--lucky", type=Path, required=True)
    args = ap.parse_args()
    prepare(args.manifest, args.work, args.lucky)
