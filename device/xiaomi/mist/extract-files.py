#!/usr/bin/env python3
"""Delegate proprietary extraction to the pinned SM4450 common tree.

The common module includes required blob/lib fixups and owns the vendor
makefiles. The 995 verified path inventory under docs/ is research only.
"""
from pathlib import Path
import os
import subprocess
import sys


def main():
    # /lineage/device/xiaomi/mist/extract-files.py -> /lineage
    source = Path(__file__).resolve()
    lineage_root = source.parents[3]
    common = lineage_root / "device/xiaomi/sm4450-common/extract-files.py"
    tool_dir = lineage_root / "tools/extract-utils"
    if not common.is_file() or not tool_dir.is_dir():
        raise SystemExit(
            "A complete LineageOS source checkout and pinned "
            "device/xiaomi/sm4450-common are required before extracting blobs.")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(tool_dir) + os.pathsep + env.get("PYTHONPATH", "")
    # Forward any source-selection arguments unchanged to upstream extract-utils.
    subprocess.run([sys.executable, str(common), *sys.argv[1:]],
                   env=env, cwd=str(lineage_root), check=True)


if __name__ == "__main__":
    main()
