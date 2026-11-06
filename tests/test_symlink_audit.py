import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_stock_links import source_path, inspect


class StockLinkTests(unittest.TestCase):
    def test_extract_source_reference(self):
        line = "-vendor/lib64/libfoo.so:vendor/lib64/libbar.so;DISABLE_DEPS"
        self.assertEqual(source_path(line), "vendor/lib64/libfoo.so")

    def test_reject_traversal(self):
        with self.assertRaises(ValueError):
            source_path("vendor/../../private")

    def test_detect_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "lib64").mkdir()
            (root / "lib64/foo.so").symlink_to("libfoo-real.so")
            result = inspect(root, "lib64/foo.so", "vendor")
            self.assertEqual(result["status"], "symlink")
            self.assertEqual(result["link_target"], "libfoo-real.so")

    def test_detect_system_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "system/lib64").mkdir(parents=True)
            (root / "system/lib64/foo.so").write_bytes(b"data")
            result = inspect(root, "lib64/foo.so", "system")
            self.assertEqual(result["status"], "regular")
            self.assertEqual(result["image_path"], "system/lib64/foo.so")


if __name__ == "__main__":
    unittest.main()
