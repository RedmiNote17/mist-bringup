import hashlib
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from pick_mirror import choose


class MirrorSelectionTests(unittest.TestCase):
    def test_select_fastest_good_host(self):
        m = {"url": "https://cdnorg.d.miui.com/test.tgz",
             "fallback_urls": ["https://bn.d.miui.com/test.tgz"]}
        stats = [
            {"host": "bad", "url": "https://bad/test.tgz",
             "valid": False, "speed_Bps": 99999999},
            {"host": "cdnorg", "url": m["url"], "valid": True, "speed_Bps": 15000000},
            {"host": "sg", "url": "https://bkt-sgp-miui-ota-update-alisgp.oss-ap-southeast-1.aliyuncs.com/test.tgz",
             "valid": True, "speed_Bps": 25000000},
        ]
        chosen = choose(m, stats)
        self.assertIn("alisgp", chosen["url"])
        self.assertEqual(len(chosen["fallback_urls"]), 1)

    def test_original_source_when_all_probes_fail(self):
        m = {"url": "https://cdnorg.d.miui.com/test.tgz",
             "fallback_urls": ["https://bn.d.miui.com/test.tgz"]}
        self.assertEqual(choose(m, [])["url"], m["url"])


if __name__ == "__main__":
    unittest.main()
