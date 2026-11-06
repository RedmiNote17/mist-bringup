#!/usr/bin/env python3
"""Read-only stock EROFS + boot analysis. Reports metadata, not proprietary binaries."""
import argparse
from contextlib import contextmanager
import csv
import gzip
import json
import lzma
import os
from pathlib import Path
import re
import stat
import subprocess
import xml.etree.ElementTree as ET

from inspect_partitions import fs_info

SENSITIVE = re.compile(r"serial|imei|meid|secret|token|password|passwd|private_key", re.I)


@contextmanager
def mounted(image, target):
    target.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["sudo", "mount", "-t", "erofs", "-o", "loop,ro,nodev,nosuid,noexec",
         str(image), str(target)], capture_output=True, text=True)
    if r.returncode == 0:
        cleanup = ["sudo", "umount", str(target)]
    else:
        f = subprocess.run(["erofsfuse", str(image), str(target)],
                           capture_output=True, text=True)
        if f.returncode:
            raise RuntimeError("Cannot mount " + image.name + ": " +
                               r.stderr[-160:] + " ; " + f.stderr[-160:])
        cleanup = ["fusermount3", "-u", str(target)]
    try:
        yield target
    finally:
        subprocess.run(cleanup, check=True)


def read_small(path, limit=524288):
    if path.is_symlink():
        return None
    try:
        if path.stat().st_size > limit:
            return None
        return path.read_text(errors="replace")
    except OSError:
        return None


def parse_prop(content, part, file, rows):
    for line in content.splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, val = [v.strip() for v in line.split("=", 1)]
        if key.startswith("ro.") and not SENSITIVE.search(key):
            rows.append({"partition": part, "file": file,
                         "key": key, "value": val[:256]})


def parse_vintf(content, part, file, rows):
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return
    for hal in root.iter("hal"):
        name = hal.findtext("name", default="")
        if name:
            rows.append({
                "partition": part, "file": file, "name": name,
                "format": hal.get("format", ""),
                "version": ",".join(x.text or "" for x in hal.findall("version")),
                "fqname": ",".join(x.text or "" for x in hal.findall("fqname")),
                "transport": hal.findtext("transport", default=""),
            })


def cpio_entries(raw):
    p = 0
    while p + 110 <= len(raw) and raw[p:p+6] in (b"070701", b"070702"):
        try:
            fields = [int(raw[p+6+i:p+14+i], 16) for i in range(0,104,8)]
        except ValueError:
            break
        size, namesize = fields[6], fields[11]
        if not 0 < namesize <= 4096 or size > 16 * 1024**2:
            break
        begin = p + 110
        data = (begin + namesize + 3) & ~3
        end = data + size
        if end > len(raw):
            break
        name = raw[begin:begin+namesize].rstrip(b"\x00").decode(errors="replace")
        if name == "TRAILER!!!":
            break
        yield name, raw[data:end]
        p = (end + 3) & ~3


def unpack_compressed(raw):
    if raw.startswith((b"070701", b"070702")):
        return raw
    if raw.startswith(b"\x1f\x8b"):
        return gzip.decompress(raw)
    if raw.startswith(b"\xfd7zXZ\x00"):
        return lzma.decompress(raw)
    if raw.startswith((b"\x04\x22\x4d\x18", b"\x02\x21\x4c\x18")):
        return subprocess.run(["lz4", "-dc"], input=raw,
                              capture_output=True, check=True).stdout
    if raw.startswith(b"\x28\xb5\x2f\xfd"):
        return subprocess.run(["zstd", "-dc"], input=raw,
                              capture_output=True, check=True).stdout
    return b""


def scan_boot(selected, report, boottool):
    bootdir = report / "boot-headers"
    bootdir.mkdir(exist_ok=True)
    ramdisk = []
    for name in ("boot", "vendor_boot", "init_boot", "recovery"):
        img = selected / (name + ".img")
        if not img.exists():
            continue
        dst = selected / ("unpack_" + name)
        call = ["python3", str(boottool), "--boot_img", str(img), "--out", str(dst)]
        out = subprocess.run(call, capture_output=True, text=True, check=True)
        (bootdir / (name + ".txt")).write_text(out.stdout)
        for file in dst.iterdir():
            if not file.is_file() or "ramdisk" not in file.name:
                continue
            if file.stat().st_size > 64 * 1024**2:
                continue
            unpacked = unpack_compressed(file.read_bytes())
            if len(unpacked) > 192 * 1024**2:
                raise ValueError("Oversized ramdisk")
            for path, data in cpio_entries(unpacked):
                base = path.rsplit("/",1)[-1].lower()
                if (base.startswith(("fstab", "init", "ueventd")) or
                    base.endswith(".prop") or base == "modules.load"):
                    if len(data) <= 524288 and b"\x00" not in data:
                        ramdisk.append("### " + name + "/" + path + "\n" +
                                       data.decode(errors="replace") + "\n")
    (report / "ramdisk-configs.txt").write_text("\n".join(ramdisk))


def analyze(work, report, boottool):
    info = json.loads((work / "preparation.json").read_text())
    report.mkdir(parents=True, exist_ok=True)
    images = sorted((work / "partitions").glob("*.img"))
    if len(images) < 8:
        raise ValueError("Eight logical partition images required")
    props, hals, blobs, counts = [], [], [], []
    with (report / "file-inventory.csv").open("w", newline="") as listing, \
         (report / "stock-init-fstab-modules.txt").open("w") as configs:
        w = csv.writer(listing)
        w.writerow(["partition", "relative_path", "bytes"])
        for img in images:
            part = img.stem.removesuffix("_a")
            if fs_info(img)["filesystem"] != "erofs":
                raise ValueError("Non-EROFS image " + img.name)
            n, modules = 0, 0
            with mounted(img, work / "mounts" / part) as root:
                for directory, dirs, files in os.walk(root, followlinks=False):
                    dirs[:] = [v for v in dirs if not (Path(directory)/v).is_symlink()]
                    for fn in files:
                        path = Path(directory) / fn
                        if path.is_symlink():
                            continue
                        try:
                            st = path.stat()
                        except OSError:
                            continue
                        if not stat.S_ISREG(st.st_mode):
                            continue
                        rel = path.relative_to(root).as_posix()
                        w.writerow([part, rel, st.st_size])
                        n += 1
                        if fn.endswith(".ko"):
                            modules += 1
                        if part in ("vendor","odm","vendor_dlkm","system_dlkm") or (
                            part in ("system_ext","mi_ext") and rel.startswith(
                                ("lib/","lib64/","bin/hw/","etc/vintf/","framework/"))):
                            blobs.append(part + "/" + rel)
                        lower = fn.lower()
                        if lower.endswith(".prop"):
                            txt = read_small(path)
                            if txt is not None:
                                parse_prop(txt, part, rel, props)
                        if lower.endswith(".xml") and "vintf/" in rel:
                            txt = read_small(path, 3_000_000)
                            if txt:
                                parse_vintf(txt, part, rel, hals)
                        if (lower.startswith(("fstab", "ueventd", "modules.")) or
                            (lower.endswith(".rc") and rel.startswith("etc/init/"))):
                            txt = read_small(path)
                            if txt is not None:
                                configs.write("### " + part + "/" + rel + "\n" + txt + "\n\n")
            counts.append({"partition": part, "files": n, "ko_modules": modules,
                           "image_bytes": img.stat().st_size})
            print("Scanned", part, n, "files;", modules, "kernel modules", flush=True)
    scan_boot(work / "selected", report, boottool)
    for name, obj in (
        ("partition-counts.json", counts), ("vintf-hals.json", hals),
        ("ro-properties.json", props)):
        (report / name).write_text(json.dumps(obj, indent=2) + "\n")
    (report / "proprietary-files-CANDIDATES.txt").write_text(
        "# Research candidates only; not a vetted proprietary-files.txt\n" +
        "\n".join(sorted(set(blobs))) + "\n")
    summary = ["# mist complete stock inventory", "",
               "Source " + info["version"] + " MD5 " + info["firmware_md5"],
               "Reference Global firmware; user's WPUMIDC.C11 not verified.", "",
               "| Partition | Files | Kernel .ko |",
               "| --- | ---: | ---: |"]
    for entry in counts:
        summary.append("| {partition} | {files} | {ko_modules} |".format(**entry))
    summary += ["", "HAL entries: " + str(len(hals)),
                "Proprietary file candidates: " + str(len(blobs)),
                "Stock read-only properties: " + str(len(props)), "",
                "No firmware binaries or flashable outputs are uploaded."]
    text = "\n".join(summary) + "\n"
    (report / "SUMMARY.md").write_text(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as stream:
            stream.write(text)
    print(text, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--boottool", type=Path, required=True)
    args = p.parse_args()
    analyze(args.work, args.report, args.boottool)
