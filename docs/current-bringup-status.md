# mist LineageOS 24.0 bring-up status

Confirmed from checksum-verified Global OS3.0.304.0.WPUMIXM:
- Stock Android boot and vendor_boot headers v4; sizes in BoardConfig are based on rawprogram partition descriptors.
- Eight EROFS logical partitions within a 10,200,547,328-byte expanded super image.
- Linux 6.6.118 declared by Xiaomi mist-w-oss source; installed kernel version not yet read from stock boot.
- lineage-24.0 exists in the public LineageOS manifest repository.

Pending work:
- Vendor/ODM VINTF, init, fstab, HAL, vendor library and module inventories from the consolidated research workflow.
- Vetted proprietary-files.txt and extracted binaries.
- Qualcomm platform integration, vendor_boot ramdisk, overlays, SELinux and A/B OTA flags.
- Real-device bootloader and custom MIDC.C11 compatibility verification.
- Compile and device testing; no flashable ROM exists yet.

The single-download workflow is .github/workflows/full-bringup.yml.
Source-derived stock information must not be confused with unverified TWRP generated settings.
