import io
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from inspect_partitions import extract_targets, fs_info


class Stage2Tests(unittest.TestCase):
    def test_ext4(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "vendor.img"
            b = bytearray(4096)
            b[1080:1082] = b"\x53\xef"
            path.write_bytes(b)
            self.assertEqual(fs_info(path)["filesystem"], "ext4")

    def test_erofs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "system.img"
            b = bytearray(4096)
            b[1024:1028] = b"\xe2\xe1\xf5\xe0"
            path.write_bytes(b)
            self.assertEqual(fs_info(path)["filesystem"], "erofs")

    def test_safe_selection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            archive = root / "fixture.tgz"
            with tarfile.open(archive, "w:gz") as tar:
                for name in ("mist/images/super.img", "mist/images/boot.img",
                             "mist/images/vendor_boot.img", "mist/images/init_boot.img",
                             "mist/images/no-op.sh"):
                    data = b"TEST"
                    entry = tarfile.TarInfo(name)
                    entry.size = len(data)
                    tar.addfile(entry, io.BytesIO(data))
            result = extract_targets(archive, root / "result")
            self.assertEqual(len(result), 4)
            self.assertEqual(sorted(p.name for p in (root/"result").iterdir()),
                             ["boot.img", "init_boot.img", "super.img", "vendor_boot.img"])


if __name__ == "__main__":
    unittest.main()
