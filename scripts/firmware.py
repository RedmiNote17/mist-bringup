#!/usr/bin/env python3
"""Read-only, checksum-validated inventory of Xiaomi mist Fastboot firmware.

No flashing, bootloader changes, firmware redistribution, or inferred BoardConfig.
The large archive is deleted after inspection.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import struct
import subprocess
import tarfile
from urllib.parse import urlparse, unquote

ALLOWED_HOSTS = {"bigota.d.miui.com", "hugeota.d.miui.com", "cdnorg.d.miui.com", "bn.d.miui.com", "bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com"}
SPARSE_MAGIC = 0xED26FF3A
MAX_ARCHIVE_BYTES = 11 * 1024**3


def validate_manifest(m):
    if m.get("codename") != "mist" or m.get("region") != "Global":
        raise ValueError("Only Global mist firmware is permitted")
    if not re.fullmatch(r"OS\d+(?:\.\d+){3}\.WPUMIXM", m.get("version", "")):
        raise ValueError("Unexpected Global firmware version format")
    filename = m.get("filename", "")
    if not re.fullmatch(r"mist_global_images_OS[0-9.]+\.WPUMIXM_[A-Za-z0-9._-]+\.tgz", filename):
        raise ValueError("Unexpected fastboot archive name")
    urls = [m.get("url", ""), *m.get("fallback_urls", [])]
    for source in urls:
        parsed = urlparse(source)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError("Firmware must come from an approved HTTPS mirror")
        if unquote(parsed.path.rsplit("/", 1)[-1]) != filename:
            raise ValueError("Manifest URL and filename disagree")
        if f"/{m['version']}/" not in parsed.path:
            raise ValueError("Manifest URL and firmware version disagree")
    if not re.fullmatch(r"[a-fA-F0-9]{32}", m.get("md5", "")):
        raise ValueError("Manifest needs a complete MD5")
    return urlparse(m["url"])


def download(m, destination):
    """Download using parallel HTTP ranges where supported; check hashes afterwards."""
    if shutil.which("aria2c") is None:
        raise RuntimeError("aria2c is required; install it before running inspection")
    destination.parent.mkdir(parents=True, exist_ok=True)
    print("Starting resumable parallel download (12 connections when supported)", flush=True)
    print(f"Source: {m['url']}", flush=True)
    args = [
        "aria2c",
        "--no-conf=true",
        "--max-connection-per-server=12",
        "--split=12",
        "--min-split-size=8M",
        "--continue=true",
        "--file-allocation=none",
        "--auto-file-renaming=false",
        "--allow-overwrite=true",
        "--max-tries=8",
        "--retry-wait=8",
        "--connect-timeout=30",
        "--timeout=120",
        "--summary-interval=20",
        "--console-log-level=notice",
        "--dir=" + str(destination.parent),
        "--out=" + destination.name,
        m["url"],
    ]
    sources = [m["url"], *m.get("fallback_urls", [])]
    for i, source in enumerate(sources, 1):
        args[-1] = source
        print(f"Mirror {i}/{len(sources)}: {urlparse(source).hostname}", flush=True)
        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as exc:
            if i < len(sources):
                print(f"Transfer failed on mirror {i}; trying alternate (exit={exc.returncode})", flush=True)
                continue
            raise
        total = destination.stat().st_size
        if total <= 0 or total > MAX_ARCHIVE_BYTES:
            raise ValueError(f"Unexpected archive size: {total} bytes")
        checksum = hashlib.md5()
        sha256 = hashlib.sha256()
        with destination.open("rb") as stream:
            while block := stream.read(16 * 1024 * 1024):
                checksum.update(block)
                sha256.update(block)
        observed = checksum.hexdigest()
        if observed.lower() == m["md5"].lower():
            print(f"MD5 verified: {observed}; bytes={total}", flush=True)
            return {"size_bytes": total, "md5": observed, "sha256": sha256.hexdigest(), "download_host": urlparse(source).hostname}
        destination.unlink(missing_ok=True)
        destination.with_name(destination.name + ".aria2").unlink(missing_ok=True)
        if i == len(sources):
            raise ValueError(f"MD5 mismatch: observed {observed}, expected {m['md5']}")
        print("Checksum mismatch; switching to alternate mirror", flush=True)
    raise RuntimeError("No mirror succeeded")


def classify_header(data):
    if data.startswith(b"ANDROID!"):
        return {"kind": "android_boot", "header_version_candidate":
                struct.unpack_from("<I", data, 40)[0] if len(data) >= 44 else None}
    if data.startswith(b"VNDRBOOT"):
        return {"kind": "vendor_boot", "header_version":
                struct.unpack_from("<I", data, 8)[0] if len(data) >= 12 else None}
    if data.startswith(b"AVB0"):
        return {"kind": "avb_vbmeta"}
    if len(data) >= 28 and struct.unpack_from("<I", data)[0] == SPARSE_MAGIC:
        magic, major, minor, file_header, chunk_header, block_sz, blocks, chunks = (
            struct.unpack_from("<IHHHHIII", data))
        return {"kind": "android_sparse", "sparse_version": f"{major}.{minor}",
                "block_size": block_sz, "expanded_bytes": blocks * block_sz,
                "chunks": chunks}
    if data.startswith(b"\x7fELF"):
        return {"kind": "elf"}
    if len(data) >= 1028 and data[1024:1028] == b"\xe2\xe1\xf5\xe0":
        return {"kind": "erofs_superblock"}
    return {"kind": "unknown"}


def safe_name(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"Unsafe archive member path: {name}")
    return p


def inspect_archive(archive, report_dir, firmware, integrity):
    report_dir.mkdir(parents=True, exist_ok=True)
    inventory, image_headers, text_count = [], {}, 0
    with tarfile.open(archive, mode="r|gz") as tar:
        for item in tar:
            if not item.isfile():
                continue
            name = safe_name(item.name)
            inventory.append({"path": str(name), "bytes": item.size})
            leaf = name.name.lower()
            keep_text = (leaf.endswith((".bat", ".sh", ".txt", ".xml", ".cfg", ".json"))
                         and item.size <= 2 * 1024 * 1024 and text_count < 200)
            if keep_text:
                stream = tar.extractfile(item)
                if stream is not None:
                    target = report_dir / "text-files" / str(name)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(stream.read(item.size))
                    text_count += 1
            elif leaf.endswith((".img", ".elf", ".bin")):
                stream = tar.extractfile(item)
                if stream is not None:
                    image_headers[str(name)] = classify_header(stream.read(4096))
            if len(inventory) % 30 == 0:
                print(f"Indexed {len(inventory)} archive files", flush=True)

    with (report_dir / "archive-files.csv").open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["path", "bytes"])
        writer.writeheader()
        writer.writerows(inventory)
    limitations = [
        "Inventory only; logical partitions inside super.img are NOT yet extracted.",
        "Boot image and vendor_boot parameters still require full unpacking.",
        "Vendor blobs, HAL/VINTF, fstab, SELinux and BoardConfig remain unverified.",
        "WPUMIDC.C11 variant is different; never flash the Global firmware on that basis."
    ]
    report = {"firmware": firmware, "integrity": integrity, "file_count": len(inventory),
              "image_headers": image_headers, "limitations": limitations}
    (report_dir / "report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# mist stock firmware inspection", "",
        f"- Firmware: `{firmware['version']}` ({firmware['region']})",
        f"- Archive: `{firmware['filename']}`",
        f"- MD5: `{integrity['md5']}` (verified)",
        f"- SHA256: `{integrity['sha256']}`",
        f"- Files inspected: **{len(inventory)}**", "",
        "## Image header signatures", "",
        "| Image | Kind | Other fields |", "| --- | --- | --- |"
    ]
    for path, detail in sorted(image_headers.items()):
        fields = ", ".join(f"{key}={value}" for key, value in detail.items() if key != "kind")
        lines.append(f"| `{Path(path).name}` | {detail['kind']} | {fields} |")
    lines += ["", "## Limitations", ""] + [f"- {note}" for note in limitations]
    summary_text = "\n".join(lines) + "\n"
    (report_dir / "SUMMARY.md").write_text(summary_text, encoding="utf-8")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(summary_text)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--working-directory", type=Path, required=True)
    parser.add_argument("--report-directory", type=Path, required=True)
    parser.add_argument("--archive", type=Path, help="Use an existing file for local tests")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    args.working_directory.mkdir(parents=True, exist_ok=True)
    args.report_directory.mkdir(parents=True, exist_ok=True)
    archive = args.archive or args.working_directory / manifest["filename"]
    try:
        if args.archive:
            total = archive.stat().st_size
            if total > MAX_ARCHIVE_BYTES:
                raise ValueError("Offline archive too large")
            data_md5 = hashlib.md5()
            data_sha = hashlib.sha256()
            with archive.open("rb") as f:
                while data := f.read(8 * 1024 * 1024):
                    data_md5.update(data)
                    data_sha.update(data)
            integrity = {"size_bytes": total, "md5": data_md5.hexdigest(),
                         "sha256": data_sha.hexdigest(), "offline_archive": True}
        else:
            integrity = download(manifest, archive)
        inspect_archive(archive, args.report_directory, manifest, integrity)
        print(f"Inspection report created in {args.report_directory}", flush=True)
    finally:
        if not args.archive:
            archive.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
