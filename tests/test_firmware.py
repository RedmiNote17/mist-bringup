"""Offline checks for the safe stock firmware inventory script."""
import io
import hashlib
import json
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from firmware import classify_header, download, inspect_archive, safe_name, validate_manifest


class FirmwareInspectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(
            (Path(__file__).resolve().parents[1] / "firmware/global-fastboot.json").read_text())

    def test_pinned_firmware(self):
        validate_manifest(self.manifest)

    def test_mismatched_region(self):
        with self.assertRaises(ValueError):
            validate_manifest({**self.manifest, "region": "China"})

    def test_mismatched_url(self):
        with self.assertRaises(ValueError):
            validate_manifest({**self.manifest, "url": "https://example.org/firmware.tgz"})

    def test_header_signatures(self):
        boot = bytearray(64)
        boot[:8] = b"ANDROID!"
        struct.pack_into("<I", boot, 40, 4)
        self.assertEqual(classify_header(boot)["header_version_candidate"], 4)
        vendor = bytearray(16)
        vendor[:8] = b"VNDRBOOT"
        struct.pack_into("<I", vendor, 8, 4)
        self.assertEqual(classify_header(vendor)["header_version"], 4)
        self.assertEqual(classify_header(b"AVB0xxxx")["kind"], "avb_vbmeta")

    def test_sparse(self):
        header = struct.pack("<IHHHHIIII", 0xED26FF3A, 1, 0, 28, 12, 4096, 100, 3, 0)
        self.assertEqual(classify_header(header)["expanded_bytes"], 409600)

    def test_reject_traversal(self):
        with self.assertRaises(ValueError):
            safe_name("../outside.txt")

    def test_streaming_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "fixture.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                for path, contents in [
                    ("mist/images/flash_all.bat", b"echo do-not-run"),
                    ("mist/images/vbmeta.img", b"AVB0" + bytes(100))]:
                    entry = tarfile.TarInfo(path)
                    entry.size = len(contents)
                    tar.addfile(entry, io.BytesIO(contents))
            report = inspect_archive(archive, root / "report", self.manifest,
                                     {"md5": "fixture", "sha256": "fixture"})
            self.assertEqual(report["file_count"], 2)
            self.assertTrue((root / "report/summary.md").exists() is False)
            self.assertTrue((root / "report/SUMMARY.md").exists())
            self.assertEqual(len(report["image_headers"]), 1)

    def test_parallel_download_and_hash(self):
        payload = b"test-fastboot-archive"
        expected_md5 = hashlib.md5(payload).hexdigest()
        def fake_run(args, check):
            self.assertTrue(check)
            self.assertEqual(args[0], "aria2c")
            self.assertIn("--split=12", args)
            self.assertIn("--max-connection-per-server=12", args)
            self.assertIn("--continue=true", args)
            name = next(a.split("=", 1)[1] for a in args if a.startswith("--out="))
            directory = next(a.split("=", 1)[1] for a in args if a.startswith("--dir="))
            (Path(directory) / name).write_bytes(payload)

        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / self.manifest["filename"]
            with patch("firmware.shutil.which", return_value="/usr/bin/aria2c"), patch(
                "firmware.subprocess.run", side_effect=fake_run
            ):
                integrity = download({**self.manifest, "md5": expected_md5}, destination)
            self.assertEqual(integrity["md5"], expected_md5)

    def test_reject_corrupt_download(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / self.manifest["filename"]
            def fake_run(args, check):
                destination.write_bytes(b"invalid checksum")
            with patch("firmware.shutil.which", return_value="/usr/bin/aria2c"), patch(
                "firmware.subprocess.run", side_effect=fake_run
            ), self.assertRaisesRegex(ValueError, "MD5 mismatch"):
                download(self.manifest, destination)


if __name__ == "__main__":
    unittest.main()
