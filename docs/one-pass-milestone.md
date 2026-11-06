# Single-run milestone and remaining hard blockers

Completed: one-pass stock extraction (MD5 verified), 8 EROFS partitions, 460 stock kernel modules,
VINTF and ramdisk inventory, 995/995 common blob paths matched, cloned common source compatibility preflight.

## Deliberate decisions

- Use the verified Global firmware for research only; do not substitute for WPUMIDC.C11 without device inspection.
- Pin the SM4450 common kernel/modules/DT repos to known source commit IDs.
- Inherit common BoardConfig rather than duplicate its complex kernel and sepolicy integration.
- Set stock super size before the common include because the common dynamic group uses immediate expansion.
- Override stock-confirmed boot and DTBO sizes; leave AVB and group handling reviewable.
- Avoid embedding proprietary binaries in Git; extract common vendor tree from supported legal device/stock source.
- Disable redundant auto-triggered validation so this commit produces one GitHub Actions preflight run.
- Never upload the full firmware to temporary GitHub artifacts while CDNORG and cache work acceptably.

## Required before first ROM

1. Review and adapt ravelin-specific vendor VINTF and audio/permission overlays to mist.
2. Confirm stock first-stage fstab, dynamic mi_ext handling, AVB indexes/signing and recovery layout.
3. Extract or otherwise obtain proprietary binaries in vendor/xiaomi/sm4450-common and apply needed fixups.
4. Build matching 6.6 kernel, modules, DTBO and vendor_boot using device-specific configs.
5. Add missing device-specific overlays, init and SELinux rules; test VINTF and dependencies.
6. Compile LineageOS 24.0, correct build errors, test on an explicitly compatible unlocked device.

A passing structural preflight must not be represented as a bootable or complete ROM.
