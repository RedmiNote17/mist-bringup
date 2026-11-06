# Redmi Note 17 5G (mist) bring-up checklist

- [x] Find published Global stock fastboot version and published MD5
- [x] Confirm Xiaomi mist-w-oss kernel branch and build metadata
- [x] Initialize RedmiNote17/mist-bringup repository
- [x] Add stock inventory workflow and offline unit tests
- [ ] Complete a successful **8.1 GB** GitHub Actions download and inventory
- [ ] Parse super.img dynamic partition metadata, filesystem formats and partition sizes
- [ ] Verify phone-specific properties, bootloader status and MIDC.C11 firmware identity
- [ ] Obtain correct proprietary vendor partitions / blobs and extract VINTF manifests
- [ ] Prepare actual device/xiaomi/mist BoardConfig, product, fstab, overlays, init and SEPolicy
- [ ] Prepare vendor/xiaomi/mist proprietary-files extraction workflow
- [ ] Integrate compatible kernel, DT/DTBO, init_boot, vendor_boot and modules
- [ ] Perform compile-only LineageOS 24.0 build on supported environment
- [ ] Validate recovery then boot on authorized unlocked test device

## Strict scope

The Global WPUMIXM images are for research. The previously reported `WPUMIDC.C11` device variant must **not** be treated as equivalent. Do not flash the research archive or extract an unverified fstab/BoardConfig and ship it as tested.
