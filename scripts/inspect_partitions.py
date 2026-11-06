#!/usr/bin/env python3
"""Read-only second-stage stock firmware report, no flashing or repackaging."""
import argparse
import csv
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import struct
import subprocess
import tarfile

from firmware import download, validate_manifest, classify_header

SELECTED = {"super.img", "boot.img", "init_boot.img", "vendor_boot.img",
            "recovery.img", "dtbo.img", "vbmeta.img", "vbmeta_system.img"}
MAX_UNPACKED = 11 * 1024**3


def extract_targets(archive: Path, output: Path):
    """Select only needed image members; never execute vendor flash scripts."""
    output.mkdir(parents=True, exist_ok=True)
    extracted = {}
    with tarfile.open(archive, "r|gz") as tar:
        for member in tar:
            name = PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or ".." in name.parts
                    or name.name not in SELECTED):
                continue
            if name.name in extracted:
                raise ValueError(f"Duplicate image in archive: {name.name}")
            if member.size <= 0 or member.size > MAX_UNPACKED:
                raise ValueError(f"Unexpected image size: {name.name}")
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError(f"Cannot read {name.name}")
            target = output / name.name
            print(f"Extracting {name.name} ({member.size / 1024**2:.1f} MiB)", flush=True)
            with target.open("wb") as out:
                shutil.copyfileobj(stream, out, length=8*1024*1024)
            if target.stat().st_size != member.size:
                raise IOError(f"Truncated image {name.name}")
            extracted[name.name] = target
    missing = {"super.img", "boot.img", "vendor_boot.img", "init_boot.img"} - set(extracted)
    if missing:
        raise ValueError(f"Missing required firmware images: {sorted(missing)}")
    return extracted


def fs_info(path: Path):
    """Recognize raw ext4/erofs/F2FS images; do not mutate filesystem contents."""
    with path.open("rb") as f:
        data = f.read(4096)
    kind = "unknown"
    if len(data) >= 1082 and data[1080:1082] == b"\x53\xef":
        kind = "ext4"
    elif len(data) >= 1028 and data[1024:1028] == b"\xe2\xe1\xf5\xe0":
        kind = "erofs"
    elif len(data) >= 1028 and data[1024:1028] == b"\x10\x20\xf5\xf2":
        kind = "f2fs"
    return {"name": path.name, "size_bytes": path.stat().st_size, "filesystem": kind}


def run_stage(manifest_path: Path, work: Path, report: Path, lucky: Path):
    manifest = json.loads(manifest_path.read_text())
    validate_manifest(manifest)
    work.mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    archive = work / manifest["filename"]
    try:
        integrity = download(manifest, archive)
        selected = extract_targets(archive, work / "selected")
        # Once extracted, the original 8GB archive is no longer required.
        archive.unlink(missing_ok=True)
        headers = {}
        for name, path in selected.items():
            with path.open("rb") as f:
                headers[name] = {"bytes": path.stat().st_size, **classify_header(f.read(4096))}
        (report/"boot-and-image-headers.json").write_text(json.dumps(headers, indent=2)+"\n")
        super_path = selected["super.img"]
        print("Listing logical partitions (sparse super, no raw expansion)", flush=True)
        listing = subprocess.run([str(lucky), "-v", "-l", str(super_path)],
                                 check=True, capture_output=True, text=True)
        (report / "super-partitions.txt").write_text(listing.stdout + "\n" + listing.stderr)
        print(listing.stdout, flush=True)
        if listing.stderr:
            print(listing.stderr, flush=True)
        print("Extracting logical partitions directly from sparse super", flush=True)
        partitions_dir = work / "partitions"
        subprocess.run([str(lucky), "-v", "-o", str(partitions_dir), str(super_path)],
                       check=True)
        image_info = [fs_info(p) for p in sorted(partitions_dir.glob("*.img"))]
        if not image_info:
            raise RuntimeError("No logical partition images extracted")
        with (report / "logical-partitions.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name","size_bytes","filesystem"])
            writer.writeheader()
            writer.writerows(image_info)
        summary = [
            "# mist stage 2: stock dynamic partition and boot research", "",
            f"Source: {manifest['version']} ({manifest['region']}); Android {manifest['android']}",
            f"MD5: `{integrity['md5']}` (verified)",
            f"SHA256: `{integrity['sha256']}`", "",
            "## Boot image signatures", "",
            "| Image | Bytes | Type | Header version (where known) |",
            "| --- | ---: | --- | ---: |"
        ]
        for name, h in sorted(headers.items()):
            summary.append(f"| {name} | {h['bytes']} | {h['kind']} | {h.get('header_version',h.get('header_version_candidate','?'))} |")
        summary += ["", "## Logical partition images", "",
                    "| Partition | Bytes | Filesystem (signature) |",
                    "| --- | ---: | --- |"]
        for part in image_info:
            summary.append(f"| {part['name']} | {part['size_bytes']} | {part['filesystem']} |")
        summary += ["", "No complete proprietary blobs or flashable image is uploaded.",
                    "WPUMIXM is a research baseline; WPUMIDC.C11 needs separate compatibility verification."]
        text = "\n".join(summary)+"\n"
        (report / "SUMMARY.md").write_text(text)
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as out:
                out.write(text)
        print(f"Finished inventory: {len(image_info)} logical partition images", flush=True)
    finally:
        archive.unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--work",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--lucky",type=Path,required=True)
    a = p.parse_args()
    run_stage(a.manifest, a.work, a.report, a.lucky)


if __name__ == "__main__":
    main()
