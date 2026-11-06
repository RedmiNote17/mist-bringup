"""Check research-derived files without downloading firmware or compiling Android."""
import csv
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class MistTreeTests(unittest.TestCase):
    def test_proprietary_sources_are_present_in_verified_inventory(self):
        inventory = set()
        import json
        audit = json.loads((ROOT / "generated/stock-global/link-audit/stock-link-audit.json").read_text())
        for entry in audit["entries"]:
            if entry["status"] in ("regular", "symlink"):
                inventory.add(entry["source"])
        with (ROOT / "generated/stock-global/file-inventory.csv").open(newline="") as f:
            for row in csv.DictReader(f):
                inventory.add(row["partition"] + "/" + row["relative_path"])
        actual = []
        for line in (ROOT / "device/xiaomi/mist/proprietary-files.txt").read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            source = line.removeprefix("-").split(";")[0].split(":")[0]
            self.assertNotIn("..", Path(source).parts)
            self.assertIn(source, inventory, "not in the stock regular-file inventory")
            actual.append(source)
        self.assertEqual(len(actual), 995)
        self.assertEqual(len(actual), len(set(actual)))

    def test_manifest_valid_and_paths_nonconflicting(self):
        xml = ET.parse(ROOT / "manifests/mist-sm4450.xml").getroot()
        self.assertEqual(xml.tag, "manifest")
        projects = xml.findall("project")
        paths = [p.attrib["path"] for p in projects]
        self.assertGreaterEqual(len(paths), 4)
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("device/xiaomi/mist", paths)
        self.assertTrue(all(len(p.attrib.get("revision", "")) == 40 for p in projects))

    def test_stock_partition_config(self):
        board = (ROOT / "device/xiaomi/mist/BoardConfig.mk").read_text()
        for expected in (
            "TARGET_BOARD_PLATFORM := parrot",
            "BOARD_BOOT_HEADER_VERSION := 4",
            "include device/xiaomi/sm4450-common/BoardConfigCommon.mk",
            "BOARD_QTI_DYNAMIC_PARTITIONS_SIZE := 10196353024",
            "BOARD_SUPER_PARTITION_SIZE := 10200547328",
            "BOARD_DTBOIMG_PARTITION_SIZE := 25165824",
            "BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296",
            "BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 100663296",
            "BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608",
            "BOARD_RECOVERYIMAGE_PARTITION_SIZE := 104857600",
        ):
            self.assertIn(expected, board)


if __name__ == "__main__":
    unittest.main()
