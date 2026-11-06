#!/usr/bin/env bash
# Copy monorepo device tree to an initialized LineageOS 24.0 source checkout.
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /path/to/lineage-24.0-source" >&2
  exit 2
fi
ROOT="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")/.." && pwd)"
if [[ ! -d "$ROOT/.repo" ]]; then
  echo "Run repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 first" >&2
  exit 1
fi
mkdir -p "$ROOT/device/xiaomi/mist"
cp -a "$HERE/device/xiaomi/mist/." "$ROOT/device/xiaomi/mist/"
echo "Preliminary tree copied; vendor, kernel and SELinux work remains."
