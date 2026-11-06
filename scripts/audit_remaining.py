#!/usr/bin/env python3
"""Offline stock-vs-common fstab, AVB, module and VINTF audit.

Uses pinned stock metadata generated from MD5-verified Xiaomi firmware.
Does NOT download firmware, extract proprietary files or produce a ROM.
"""
import argparse
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMMON_LOAD = {
    "vendor_boot": "modules.load.vendorboot",
    "vendor_dlkm": "modules.load",
    "system_dlkm": "modules.load.system_dlkm",
}
STOCK_LOAD = {
    "vendor_boot": ("ramdisk", "vendor_boot/lib/modules/modules.load"),
    "vendor_dlkm": ("configs", "vendor_dlkm/lib/modules/modules.load"),
    "system_dlkm": ("configs", "system_dlkm/flatten/lib/modules/modules.load"),
}


def section(text, title):
    mark = "### " + title + "\n"
    idx = text.find(mark)
    if idx < 0:
        raise ValueError("Missing stock config section: " + title)
    remaining = text[idx + len(mark):]
    next_header = re.search(r"(?m)^### ", remaining)
    return remaining[:next_header.start()] if next_header else remaining


def modules(contents):
    return [row.strip().split()[0] for row in contents.splitlines()
            if row.strip() and not row.lstrip().startswith("#")
            and row.strip().split()[0].endswith(".ko")]


def fstab(contents):
    rows = []
    for row in contents.splitlines():
        row = row.strip()
        if not row or row.startswith("#"):
            continue
        fields = row.split()
        if len(fields) >= 5:
            device, mountpoint, fs, flags, options = fields[:5]
            rows.append({"device": device, "mount": mountpoint, "fs": fs,
                         "flags": flags, "options": options})
    return rows


def delta(stock, common):
    s, c = set(stock), set(common)
    return {
        "stock_entries": len(stock),
        "common_entries": len(common),
        "matching_names": len(s & c),
        "stock_only": sorted(s - c),
        "common_only": sorted(c - s),
        "stock_duplicates": sorted({x for x in s if stock.count(x) > 1}),
    }


def audit(common, report):
    text_ramdisk = (ROOT / "generated/stock-global/ramdisk-configs.txt").read_text()
    text_configs = (ROOT / "generated/stock-global/stock-init-fstab-modules.txt").read_text()
    comparison, blockers = {}, []
    for category, (source, path) in STOCK_LOAD.items():
        original = modules(section(
            text_ramdisk if source == "ramdisk" else text_configs, path))
        upstream = modules((common / "configs/modules" / COMMON_LOAD[category]).read_text())
        if not original or not upstream:
            raise ValueError("Empty kernel module load list: " + category)
        comparison[category] = delta(original, upstream)
        if comparison[category]["stock_only"] or comparison[category]["common_only"]:
            blockers.append(category + ": stock/common kernel module names differ; validate "
                            "compiled modules and load order on mist before any boot test")
    rows = fstab(section(text_ramdisk, "vendor_boot/first_stage_ramdisk/fstab.default"))
    if len(rows) < 20:
        raise ValueError("Unexpectedly short vendor_boot first-stage fstab")
    dynamic = {}
    for row in rows:
        if "logical" in row["options"].split(","):
            dynamic.setdefault(row["device"], set()).add(row["fs"])
    partitions = json.loads(
        (ROOT / "generated/stock-global/partition-counts.json").read_text())
    names = {p["partition"] for p in partitions}
    expected = {"system","system_ext","product","vendor","vendor_dlkm",
                "system_dlkm","odm","mi_ext"}
    if names != expected or expected - set(dynamic):
        raise ValueError("Stock super partitions and first-stage fstab disagree")
    if any("erofs" not in dynamic[p] for p in expected):
        raise ValueError("Stock EROFS mount missing")
    chain = {"boot","init_boot","vendor_boot","dtbo","recovery"}
    observed_chain = {
        r["mount"].lstrip("/") for r in rows
        if r["device"].startswith("/dev/block") and r["mount"].lstrip("/") in chain
    }
    if chain != observed_chain:
        raise ValueError("Boot-chain AVB mount entries incomplete")
    for mount in ("/data", "/metadata"):
        if not any(r["mount"] == mount and r["fs"] == "f2fs" for r in rows):
            raise ValueError("Expected stock F2FS mount absent: " + mount)
    if not any(r["mount"] == "/data" and "fileencryption=" in r["options"] for r in rows):
        raise ValueError("Stock userdata file encryption evidence absent")
    c_fstab = fstab((common / "init/fstab.qcom").read_text())
    if not c_fstab:
        raise ValueError("Pinned common fstab not found")
    hals = json.loads((ROOT / "generated/stock-global/vintf-hals.json").read_text())
    odm_variants = sorted({x["file"] for x in hals if x["partition"] == "odm"
                           and x["file"].startswith("etc/vintf/manifest_")})
    vendor_variants = sorted({x["file"] for x in hals if x["partition"] == "vendor"
                              and x["file"] in (
                                  "etc/vintf/manifest_parrot.xml",
                                  "etc/vintf/manifest_ravelin.xml")})
    if not odm_variants or len(vendor_variants) != 2:
        raise ValueError("Stock VINTF variant inventory incomplete")
    common_manifest = (common / "configs/vintf/manifest_ravelin.xml").read_text()
    if "IGatekeeper" not in common_manifest:
        raise ValueError("Pinned shared manifest changed")
    common_mk = (common / "common.mk").read_text()
    if "sku_ravelin" in common_mk:
        blockers.append("Shared audio and permissions use sku_ravelin: choose actual mist SKU")
    blockers.extend([
        "Stock mi_ext supplies system/product bind and overlay mounts; plan removal "
        "or preservation when writing LineageOS dynamic partitions",
        "Stock mount table uses AVB chains and encrypted F2FS: "
        "validate recovery, vbmeta and first-stage mount behavior",
        "Select actual active ODM/VINTF/NFC/SIM variant, not all 1180 HAL entries",
        "Different module lists are not interchangeable without verifying "
        "kernel build, ABI, dependencies and module order",
        "Full vendor ELF/Soong, sepolicy and hardware runtime still need build tests",
        "The reported WPUMIDC.C11 phone remains unverified against Global WPUMIXM",
    ])
    result = {
        "status": "stock_evidence_verified_not_flashable",
        "firmware_downloaded": False,
        "stock_firmware": "OS3.0.304.0.WPUMIXM",
        "module_comparison": comparison,
        "first_stage_fstab": {
            "entries": len(rows),
            "logical_partitions": {k: sorted(v) for k, v in sorted(dynamic.items())},
            "boot_chain": sorted(observed_chain),
            "data_filesystem": "f2fs",
            "metadata_filesystem": "f2fs",
            "data_fileencryption": True,
            "common_entries": len(c_fstab),
        },
        "vintf": {
            "all_variant_entries": len(hals),
            "odm_variants": odm_variants,
            "vendor_variants": vendor_variants,
            "selected_variant": None,
        },
        "unresolved": blockers,
        "rom_built": False, "boot_tested": False,
    }
    report.mkdir(parents=True, exist_ok=True)
    (report / "remaining-hardware-audit.json").write_text(
        json.dumps(result, indent=2) + "\n")
    summary = [
        "# Redmi Note 17 mist: consolidated hardware checks", "",
        "All stock evidence comes from verified published metadata. No firmware downloaded.",
        "", "## Kernel module load list comparison", "",
        "| Load list | Stock entries | Common entries | Stock-only | Common-only |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for category, stats in comparison.items():
        summary.append(
            f"| {category} | {stats['stock_entries']} | {stats['common_entries']} | "
            f"{len(stats['stock_only'])} | {len(stats['common_only'])} |")
    summary += [
        "", f"Stock first-stage mounts: {len(rows)}",
        "Logical EROFS: " + ", ".join(sorted(dynamic)),
        "AVB boot entries: " + ", ".join(sorted(observed_chain)),
        "Userdata and metadata: F2FS, with file encryption on userdata.",
        f"VINTF entries (includes inactive variants): {len(hals)}",
        "ODM variants: " + str(len(odm_variants)),
        "Vendor manifests: " + ", ".join(vendor_variants),
        "", "## Remaining boot/build blockers", "",
    ]
    summary.extend("- " + b for b in blockers)
    summary += ["", "No bootable/flashable LineageOS build has been created.", ""]
    output = "\n".join(summary)
    (report / "HARDWARE-AUDIT.md").write_text(output)
    print(output, flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as fp:
            fp.write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--common", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    audit(args.common, args.report)
