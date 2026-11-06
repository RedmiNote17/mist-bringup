import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_remaining import section, modules, fstab, delta


class HardwareAuditTests(unittest.TestCase):
    def test_sections(self):
        self.assertEqual(section("### one\na.ko\n### two\nb.ko\n", "one").strip(), "a.ko")

    def test_modules(self):
        self.assertEqual(modules("# comment\na.ko\nnotmodule\n b.ko\n"),
                         ["a.ko","b.ko"])

    def test_fstab(self):
        self.assertEqual(fstab("system /system erofs ro wait,logical,first_stage_mount\n")[0]["fs"],
                         "erofs")

    def test_diff(self):
        data = delta(["a.ko","b.ko","b.ko"],["a.ko","c.ko"])
        self.assertEqual(data["stock_only"], ["b.ko"])
        self.assertEqual(data["common_only"], ["c.ko"])
        self.assertEqual(data["stock_duplicates"], ["b.ko"])


if __name__ == "__main__":
    unittest.main()
