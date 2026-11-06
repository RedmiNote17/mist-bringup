#!/usr/bin/env python3
"""Offline, evidence-based LineageOS mist integration preflight.

Read published metadata and one pinned upstream common tree. No ROM, firmware,
device flashing, proprietary binaries, or large download required.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SUPER_SIZE = 10200547328
GROUP_SIZE = SUPER_SIZE - 4194304
UPSTREAM_COMMON_SHA = "a476fff00d6149fc988f12f43b73cde1587c7b88"
EXPECTED = {
    "BOARD_SUPER_PARTITION_SIZE": SUPER_SIZE,
    "BOARD_QTI_DYNAMIC_PARTITIONS_SIZE": GROUP_SIZE,
    "BOARD_BOOT_HEADER_VERSION": 4,
    "BOARD_BOOTIMAGE_PARTITION_SIZE": 100663296,
    "BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE": 100663296,
    "BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE": 8388608,
    "BOARD_RECOVERYIMAGE_PARTITION_SIZE": 104857600,
    "BOARD_DTBOIMG_PARTITION_SIZE": 25165824,
}
PROJECT_PATHS = {
    "device/xiaomi/sm4450-common",
    "kernel/xiaomi/sm4450",
    "kernel/xiaomi/sm4450-modules",
    "kernel/xiaomi/sm4450-devicetrees",
}


def read_make_number(contents, name):
    pattern = r"(?m)^\s*" + re.escape(name) + r"\s*(?::=|=)\s*(\d+)\s*(?:#.*)?$"
    found = re.findall(pattern, contents)
    if len(found) != 1:
        raise ValueError("Expected one definition for " + name)
    return int(found[0])


def proprietary_sources(path):
    src = []
    for line in path.read_text().splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        key = entry.removeprefix("-").split(";", 1)[0].split(":", 1)[0]
        if key.startswith("/") or ".." in Path(key).parts or not key:
            raise ValueError("Invalid proprietary path " + key)
        src.append(key)
    return src


def inventory_paths():
    paths = set()
    with (ROOT / "generated/stock-global/file-inventory.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            paths.add(row["partition"] + "/" + row["relative_path"])
    audit = json.loads(
        (ROOT / "generated/stock-global/link-audit/stock-link-audit.json").read_text())
    assert audit["firmware_md5"] == "c4450c4e168052ca9de1211306d3beff"
    for entry in audit["entries"]:
        if entry["status"] in ("regular", "symlink"):
            paths.add(entry["source"])
    return paths


def analyze(common):
    issues = []
    info = []
    board = (ROOT / "device/xiaomi/mist/BoardConfig.mk").read_text()
    dev = (ROOT / "device/xiaomi/mist/device.mk").read_text()
    product = (ROOT / "device/xiaomi/mist/lineage_mist.mk").read_text()
    for key, size in EXPECTED.items():
        actual = read_make_number(board, key)
        if actual != size:
            raise ValueError(f"{key}: expected stock {size}, got {actual}")
    cinclude = "include device/xiaomi/sm4450-common/BoardConfigCommon.mk"
    if board.count(cinclude) != 1:
        raise ValueError("Shared SM4450 BoardConfig must be inherited once")
    if board.index("BOARD_SUPER_PARTITION_SIZE :=") > board.index(cinclude):
        raise ValueError("Super size must precede common config (:= expansion)")
    if "BOARD_BOOTIMG_HEADER_VERSION" in board:
        raise ValueError("Incorrect Android boot-header variable present")
    if "$(call inherit-product, device/xiaomi/sm4450-common/common.mk)" not in dev:
        raise ValueError("Device product is not inheriting SM4450 common")
    if "device/xiaomi/mist/device.mk" not in product:
        raise ValueError("Lineage product does not inherit mist device")
    if "PRODUCT_DEVICE := mist" not in product:
        raise ValueError("Wrong Android product device codename")
    info.append("Common BoardConfig and product makefile inheritance: consistent")
    info.append("Stock boot, recovery, DTBO and super partition sizes: consistent")

    tree = ET.parse(ROOT / "manifests/mist-sm4450.xml").getroot()
    projects = tree.findall("project")
    paths = {e.attrib["path"] for e in projects}
    if paths != PROJECT_PATHS:
        raise ValueError("Common/kernel/modules/DT project set mismatch")
    for project in projects:
        if not re.fullmatch(r"[a-f0-9]{40}", project.attrib["revision"]):
            raise ValueError("Unpinned dependency: " + project.attrib["name"])
    if not common.is_dir():
        raise ValueError("Pinned SM4450 common source missing")
    cb = (common / "BoardConfigCommon.mk").read_text()
    cm = (common / "common.mk").read_text()
    if "TARGET_BOARD_PLATFORM := parrot" not in cb or "TARGET_KERNEL_VERSION := 6.6" not in cb:
        raise ValueError("Unexpected shared Qualcomm/6.6 BoardConfig contract")
    if "BOARD_SUPER_PARTITION_GROUPS := qti_dynamic_partitions" not in cb:
        raise ValueError("Unexpected common dynamic partitions")
    if "vendor/xiaomi/sm4450-common/BoardConfigVendor.mk" not in cb:
        raise ValueError("Common tree changed expected vendor BoardConfig")
    if "vendor/xiaomi/sm4450-common/sm4450-common-vendor.mk" not in cm:
        raise ValueError("Common tree changed expected vendor makefile")
    # Device-specific manifest overrides the shared ravelin-named source.
    if "DEVICE_MANIFEST_FILE :=" not in dev or "$(DEVICE_PATH)/configs/vintf/manifest.xml" not in dev:
        raise ValueError("mist device manifest override missing")
    path = ROOT / "device/xiaomi/mist/configs/vintf/manifest.xml"
    vm = ET.parse(path).getroot()
    if vm.tag != "manifest" or vm.attrib.get("type") != "device":
        raise ValueError("Invalid mist device VINTF manifest")
    got = {(hal.findtext("name"), fq.text)
           for hal in vm.findall("hal") for fq in hal.findall("fqname")}
    verified = {
        ("android.hardware.gatekeeper", "IGatekeeper/default"),
        ("android.hardware.drm", "IDrmFactory/wfdhdcp"),
        ("vendor.qti.hardware.wifidisplaysession_aidl", "IWifiDisplaySession/default"),
        ("vendor.qti.hardware.wifidisplaysession_aidl", "IWifiDisplaySessionAudioTrack/default"),
        ("vendor.qti.hardware.wifidisplaysession_aidl", "IWifiDisplaySessionImageTrack/default"),
        ("vendor.qti.hardware.wifidisplaysession_aidl", "IWifiDisplaySessionVideoTrack/default"),
    }
    stock = json.loads((ROOT / "generated/stock-global/vintf-hals.json").read_text())
    observed = {(s["name"], f.strip())
                for s in stock if s["partition"] == "vendor"
                and s["file"] == "etc/vintf/manifest_parrot.xml"
                for f in s["fqname"].split(",") if f.strip()}
    if verified != got or not got.issubset(observed):
        raise ValueError("mist VINTF interfaces differ from verified stock parrot manifest")
    info.append("mist device VINTF manifest overrides ravelin and matches 6 stock HAL instances")
    if "sku_ravelin" in cm:
        issues.append("Common audio/permissions use sku_ravelin; substitute verified mist SKU")
    info.append("Pinned SM4450 common tree supports parrot/Linux 6.6 and shared vendor modules")

    src = proprietary_sources(ROOT / "docs/verified-global-proprietary-files.txt")
    if len(src) != 995 or len(set(src)) != len(src):
        raise ValueError("Expected exactly 995 unique stock-verified proprietary paths")
    unavailable = sorted(set(src) - inventory_paths())
    if unavailable:
        raise ValueError(f"Stock path evidence missing for {len(unavailable)} files")
    info.append("All 995 common-tree proprietary source paths exist in verified Global stock")

    counts = json.loads(
        (ROOT / "generated/stock-global/partition-counts.json").read_text())
    modules = sum(p["ko_modules"] for p in counts)
    if len(counts) != 8 or modules != 460:
        raise ValueError(f"Unexpected stock logical partitions/modules: {len(counts)}/{modules}")
    if any(p["partition"] == "mi_ext" for p in counts):
        issues.append("Stock mi_ext is not in LineageOS dynamic group; decide preservation/removal on device")
    info.append(f"Stock logical partitions: {len(counts)}; kernel modules: {modules}")

    v = json.loads((ROOT / "generated/stock-global/vintf-hals.json").read_text())
    info.append(f"Published VINTF entries: {len(v)} (includes inactive stock variants)")
    if len(v) < 100:
        raise ValueError("VINTF inventory unexpectedly incomplete")
    boot = (ROOT / "generated/stock-global/boot-headers/vendor_boot.txt").read_text()
    if "vendor boot image header version: 4" not in boot:
        raise ValueError("Stock vendor_boot header v4 not confirmed")
    ramdisk = (ROOT / "generated/stock-global/ramdisk-configs.txt").read_text()
    if "### vendor_boot/first_stage_ramdisk/fstab.default" not in ramdisk:
        raise ValueError("Stock vendor_boot fstab missing")
    issues += [
        "Validate effective VINTF service registration, init/first-stage fstab and SELinux on-device",
        "Extract common vendor blobs to vendor/xiaomi/sm4450-common; no binaries are in this repo",
        "Validate exact kernel/modules, recovery, AVB, OTA, display, camera and modem runtime",
        "Compare test phone WPUMIDC.C11 against WPUMIXM stock reference before flashing",
        "Full LineageOS 24.0 source sync, compile and real-device boot test not performed",
    ]
    return info, issues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--common", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    passed, blockers = analyze(args.common)
    args.report.mkdir(parents=True, exist_ok=True)
    data = {
        "status": "structural_preflight_passed_rom_not_boot_validated",
        "stock_firmware": "OS3.0.304.0.WPUMIXM",
        "verified_firmware_md5": "c4450c4e168052ca9de1211306d3beff",
        "common_commit": UPSTREAM_COMMON_SHA,
        "passed": passed, "boot_blockers": blockers,
        "full_rom_built": False, "flashable": False,
        "firmware_downloaded": False,
    }
    (args.report / "preflight.json").write_text(json.dumps(data, indent=2) + "\n")
    lines = ["# Redmi Note 17 mist LineageOS 24.0 consolidated preflight", "",
             "Result: structural checks PASSED. ROM build and boot compatibility NOT verified.",
             "", "## Verified", ""]
    lines.extend("- " + s for s in passed)
    lines += ["", "## Outstanding release blockers", ""]
    lines.extend("- " + s for s in blockers)
    lines += ["", "This check uses repository stock metadata and a shallow pinned "
              "common-tree checkout; it never downloads the firmware.", ""]
    summary = "\n".join(lines)
    (args.report / "SUMMARY.md").write_text(summary)
    print(summary, flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary)


if __name__ == "__main__":
    main()
