# Redmi Note 17 5G (mist) — LineageOS bring-up

> **Status:** stock-firmware research and inventory. **Not a bootable ROM. Not for flashing.**

This repository belongs to the [RedmiNote17](https://github.com/RedmiNote17) organization and is the staging area for an unofficial LineageOS 24.0 / Android 17 bring-up for **mist**.

## Firmware reference

- **Region:** Global (WPUMIXM)
- **Fastboot release:** OS3.0.304.0.WPUMIXM (Android 16, 2026-09-17)
- **Official Xiaomi CDN:** configured in `firmware/global-fastboot.json`; MD5 checked before inventory.
- **Important:** the device was previously reported as `WPUMIDC.C11`. **This is not the same as WPUMIXM.** The Global firmware is used only to research stock layouts; do not flash or substitute regional firmware files.

## What gets built here

The GitHub Actions inspection workflow downloads the published fastboot archive from Xiaomi, validates its MD5, safely inventories members and image headers, and uploads **small diagnostic reports only**. It does not upload the proprietary firmware, flash anything, change a bootloader, or claim the device is supported by LineageOS.

See `docs/bringup-checklist.md` for the staged roadmap and unresolved requirements.

### Xiaomi upstream sources

- Kernel: https://github.com/MiCode/Xiaomi_Kernel_OpenSource/tree/mist-w-oss
- Kernel build tooling: https://github.com/MiCode/kernel_build/tree/mist-w-oss
- Device-tree kernel code: https://github.com/MiCode/kernel_devicetree/tree/mist-w-oss

The inspected Xiaomi kernel Makefile declares Linux **6.6.118** and the mist config requests boot image header v4, init_boot and vendor_dlkm. These do **not** establish every required Android BoardConfig setting.

### Sources for the pinned Global fastboot reference

- https://xmfirmwareupdater.com/hyperos/mist/stable/OS3.0.304.0.WPUMIXM/
- https://mirom.ezbox.idv.tw/en/phone/mist/

**No flashable artifacts are produced by this repository.**

## Download performance

The inspection workflow uses **aria2c** with up to **12 HTTP range connections**, retry/resume support, and progress summaries every 20 seconds. Range support and actual throughput depend on Xiaomi's CDN; faster downloads are not guaranteed. The final MD5 remains mandatory, and the full firmware is never published as a workflow artifact.
