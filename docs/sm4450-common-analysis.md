# LineageOS 24.0 SM4450 shared-hardware reference

Relevant upstream public reference: [xiaomi-ravelin/android_device_xiaomi_sm4450-common](https://github.com/xiaomi-ravelin/android_device_xiaomi_sm4450-common/tree/lineage-24.0).

## Why it may help mist

- Xiaomi mist-w-oss source refers to SM4450/Parrot.
- The reference common tree targets Qualcomm parrot with Linux 6.6, GKI and dynamic A/B partitions.
- Its common BoardConfig shows boot header v4 and a 96 MiB boot image, consistent with the verified mist stock boot image.
- It supplies kernel, modules, device-tree, sepolicy, HAL and init integration examples on lineage-24.0.

## Why not to copy it blindly

- Its product configuration explicitly references **sku_ravelin** audio configurations; mist audio hardware and SKU must be verified.
- Its `dtbo` size (0x1700000) does not equal the verified mist dtbo partition size (25,165,824 bytes).
- The mist stock super partition contains an extra **mi_ext** logical partition not present in the common tree's generic dynamic partition list.
- AVB rollback/signing rules, fstab, hardware manifests, kernel modules and SEPolicy must come from matching stock images.
- This common tree is a starting reference rather than tested Redmi Note 17 5G support.

## Dependency source repositories listed by that common tree

- xiaomi-ravelin/android_kernel_xiaomi_sm4450
- xiaomi-ravelin/android_kernel_xiaomi_sm4450-modules
- xiaomi-ravelin/android_kernel_xiaomi_sm4450-devicetrees
- LineageOS/android_hardware_xiaomi (dependency metadata)

All of the above need a compatibility review and properly installed branches before we inherit the common tree. No unverified hardware settings are added to our mist BoardConfig yet.

## Additional direct mist evidence

- The common repository's `proprietary-files.txt` explicitly says its default blob list came from **mist OS3.0.306.0.WPUINXM** (India).
- Its `init/init.kernel.post_boot.sh` contains conditional handling when `ro.product.name` is `mist`.
- This provides a strong candidate reference for the Redmi Note 17 project, but the Indian build differs from our checksum-verified Global WPUMIXM source. We should intersect its file paths with our Global EROFS inventory, not blindly reuse or redistribute those proprietary binaries.
