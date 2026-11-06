# Redmi Note 17 mist LineageOS 24.0 consolidated preflight

Result: structural checks PASSED. ROM build and boot compatibility NOT verified.

## Verified

- Common BoardConfig and product makefile inheritance: consistent
- Stock boot, recovery, DTBO and super partition sizes: consistent
- mist device VINTF manifest overrides ravelin and matches 6 stock HAL instances
- Pinned SM4450 common tree supports parrot/Linux 6.6 and shared vendor modules
- All 995 common-tree proprietary source paths exist in verified Global stock
- Stock logical partitions: 8; kernel modules: 460
- Published VINTF entries: 1180 (includes inactive stock variants)

## Outstanding release blockers

- Common audio/permissions use sku_ravelin; substitute verified mist SKU
- Stock mi_ext is not in LineageOS dynamic group; decide preservation/removal on device
- Validate effective VINTF service registration, init/first-stage fstab and SELinux on-device
- Extract common vendor blobs to vendor/xiaomi/sm4450-common; no binaries are in this repo
- Validate exact kernel/modules, recovery, AVB, OTA, display, camera and modem runtime
- Compare test phone WPUMIDC.C11 against WPUMIXM stock reference before flashing
- Full LineageOS 24.0 source sync, compile and real-device boot test not performed

This check uses repository stock metadata and a shallow pinned common-tree checkout; it never downloads the firmware.
