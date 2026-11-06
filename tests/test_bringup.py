import gzip
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from analyze_stock import parse_prop, parse_vintf, unpack_compressed


class StockAnalysisTests(unittest.TestCase):
    def test_properties_redacted(self):
        rows = []
        parse_prop("ro.product.device=mist\nro.serialno=SECRET\npersist.sys.foo=bar",
                   "vendor", "build.prop", rows)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["value"], "mist")

    def test_vintf(self):
        rows = []
        parse_vintf(
            '<manifest><hal format="aidl"><name>android.hardware.audio.core</name>'
            '<fqname>IModule/default</fqname></hal></manifest>',
            "vendor", "etc/vintf/manifest.xml", rows)
        self.assertEqual(rows[0]["name"], "android.hardware.audio.core")

    def test_gzip(self):
        self.assertEqual(unpack_compressed(gzip.compress(b"070701xxx")),
                         b"070701xxx")


if __name__ == "__main__":
    unittest.main()
