# nAa-mist canonical repository ownership and migration handover

**Research home:** [nAa-mist/mist-bringup](https://github.com/nAa-mist/mist-bringup).

This repository retains the original **28 pre-split source commits**, firmware
download testing, verified stock inventories, symlink audits, and hardware
compatibility reports. All future device, vendor, and kernel source fixes must
be made in the corresponding **nAa-mist** repository, not here.

## Source ownership

| Repository | Intended LineageOS checkout | Status |
| --- | --- | --- |
| [device_xiaomi_mist](https://github.com/nAa-mist/device_xiaomi_mist) | `device/xiaomi/mist` | All eight original device revisions replayed; current tree and CI validated |
| [vendor_xiaomi_mist](https://github.com/nAa-mist/vendor_xiaomi_mist) | `vendor/xiaomi/mist` | Mist-only vendor placeholder; no extracted binary |
| [device_xiaomi_sm4450-common](https://github.com/nAa-mist/device_xiaomi_sm4450-common) | `device/xiaomi/sm4450-common` | Complete 57-file imported shared common source |
| [vendor_xiaomi_sm4450-common](https://github.com/nAa-mist/vendor_xiaomi_sm4450-common) | `vendor/xiaomi/sm4450-common` | Vendor makefile scaffold; extraction pending |
| [kernel_xiaomi_sm4450](https://github.com/nAa-mist/kernel_xiaomi_sm4450) | `kernel/xiaomi/sm4450` | **Not yet imported**; placeholder for core source |
| [kernel_xiaomi_sm4450-modules](https://github.com/nAa-mist/kernel_xiaomi_sm4450-modules) | `kernel/xiaomi/sm4450-modules` | 8,966 pinned upstream files imported |
| [kernel_xiaomi_sm4450-devicetrees](https://github.com/nAa-mist/kernel_xiaomi_sm4450-devicetrees) | `kernel/xiaomi/sm4450-devicetrees` | 7,026 pinned upstream files imported |
| [kernel_xiaomi_mist](https://github.com/nAa-mist/kernel_xiaomi_mist) | `kernel/xiaomi/mist` (planned) | User will upload complete mist kernel source |
| [mist-bringup](https://github.com/nAa-mist/mist-bringup) | Research only, not a LineageOS source project | Firmware analysis, original history and reports |

## Upstream source pin provenance

- Common device: `xiaomi-ravelin/android_device_xiaomi_sm4450-common` at `a476fff00d6149fc988f12f43b73cde1587c7b88`; 57 upstream files confirmed identical after import.
- SM4450 modules: `xiaomi-ravelin/android_kernel_xiaomi_sm4450-modules` at `23a3d2ac880e7f1f8185fd86abb7a8ff94d24ec3`; 8,966 paths imported through verified snapshot workflow.
- SM4450 DT: `xiaomi-ravelin/android_kernel_xiaomi_sm4450-devicetrees` at `da6aa48e7f1ab75dfaff618fa2339940d85d8e04`; 7,026 paths imported through verified snapshot workflow.
- **Temporary core kernel:** `xiaomi-ravelin/android_kernel_xiaomi_sm4450` at `f879c1be9822631de45f9ef4a5db5a98729dd180`; remains external until the owner's original mist kernel upload and compatibility review.

Current reproducible dependency manifest (canonical):
[device_xiaomi_mist/manifests/mist-sm4450.xml](https://github.com/nAa-mist/device_xiaomi_mist/blob/main/manifests/mist-sm4450.xml).
The device itself tracks `main`; other source dependencies use full pinned
commit SHAs. To pick up a new common/module/DT fix, bump the pin **in the device
repository**, not the research archive.

## Migration history

The original 28 historical commits are preserved here, without force-pushing.
All eight original device-tree-changing commits were replayed in the new device
repo in chronological order with original SHA references. Research scripts and
tests used by the device were copied into its own CI system. Different repo
roots mean different downstream commit SHAs; this does not delete original
history.

The source `kernel/xiaomi/mist/README.md` placeholder was replayed to the
kernel-specific repo. Research scripts and generated reports intentionally stay here.
The original mixed-device preflight workflow is manual-only; current source
validation runs inside each respective repo.

## Before a bootable ROM

The shared/vendor scaffolds are **not** a complete extracted vendor tree.
Kernel integration, active SKU audio/VINTF, module ordering, first-stage F2FS,
AVB, SEPolicy, full Android compilation and on-device testing remain incomplete.
The owner's reported customized WPUMIDC.C11 device must not be assumed to match
the Global WPUMIXM research firmware.

**Next external input:** the user can upload the full mist kernel source to
[kernel_xiaomi_mist](https://github.com/nAa-mist/kernel_xiaomi_mist), following
[KERNEL_UPLOAD.md](https://github.com/nAa-mist/kernel_xiaomi_mist/blob/main/KERNEL_UPLOAD.md).
No repeated large Xiaomi firmware download is needed merely to review the kernel.
