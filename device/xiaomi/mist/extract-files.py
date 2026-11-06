#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
# SPDX-License-Identifier: Apache-2.0
"""LineageOS extraction entrypoint. Requires a reviewed proprietary-files.txt."""
from extract_utils.main import ExtractUtils, ExtractUtilsModule

module = ExtractUtilsModule("mist", "xiaomi")

if __name__ == "__main__":
    ExtractUtils.device(module).run()
