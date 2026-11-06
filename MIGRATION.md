# nAa-mist repository migration and historical preservation

The original combined mist bring-up project was developed in this repository.
It contains **28 original commits**, including the full history of all GitHub Actions
firmware benchmark work, stock inventories, and the initial device/vendor trees.
No original commit, file revision or generated research report was deleted.

## Current ownership — do not develop the device tree here

| Work | Canonical repository | LineageOS checkout path |
| --- | --- | --- |
| Device product, BoardConfig, VINTF, extraction, tests | [nAa-mist/device_xiaomi_mist](https://github.com/nAa-mist/device_xiaomi_mist) | `device/xiaomi/mist` |
| Device-specific vendor overlays / future extra blobs | [nAa-mist/vendor_xiaomi_mist](https://github.com/nAa-mist/vendor_xiaomi_mist) | `vendor/xiaomi/mist` |
| Stock inspection, original Git history and reports | [nAa-mist/mist-bringup](https://github.com/nAa-mist/mist-bringup) | Research-only |

Device tree: all **eight original device-touching revisions** were replayed in
chronological order with source SHA references in commit messages. The latest
eight device files were verified to have byte-identical Git blob SHAs at migration.
The 995-entry verified common proprietary-path research list was transferred
to the device repo under `docs/verified-global-proprietary-files.txt`, and the
device's original tests and preflight scripts now run in its own Actions workflow.

Vendor tree: the initial vendor skeleton revision was reproduced and extended
with mist-only placeholder configuration. Vendor shared SM4450 blobs are **not**
fabricated or committed here. They remain an independent common vendor
extraction dependency.

New history hashes necessarily differ because repository parent commits and
tree roots differ. This is why **the original 28-commit Git graph is preserved
here** rather than rewritten or force-pushed.

## Research workflows

Research benchmark, firmware inspection, and text report generation remain
here for reference. The old mixed device/preflight workflow is now manual-only.
The active device CI pipeline is
[device_xiaomi_mist Actions](https://github.com/nAa-mist/device_xiaomi_mist/actions).

No new full firmware archive is uploaded to these repositories. The verified
metadata and partition cache can be reused while available.

## Shared SM4450 dependencies

The research source manifest currently points to upstream xiaomi-ravelin
SM4450 common, kernel, modules, and devicetree sources. They have not yet
been migrated into nAa-mist-owned repositories. The correct platform is
**SM4450 / Qualcomm Parrot**, not "SM440".
