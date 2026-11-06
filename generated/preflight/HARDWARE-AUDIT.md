# Redmi Note 17 mist: consolidated hardware checks

All stock evidence comes from verified published metadata. No firmware downloaded.

## Kernel module load list comparison

| Load list | Stock entries | Common entries | Stock-only | Common-only |
| --- | ---: | ---: | ---: | ---: |
| vendor_boot | 110 | 86 | 23 | 1 |
| vendor_dlkm | 350 | 232 | 37 | 1 |
| system_dlkm | 78 | 77 | 1 | 0 |

Stock first-stage mounts: 54
Logical EROFS: mi_ext, odm, product, system, system_dlkm, system_ext, vendor, vendor_dlkm
AVB boot entries: boot, dtbo, init_boot, recovery, vendor_boot
Userdata and metadata: F2FS, with file encryption on userdata.
VINTF entries (includes inactive variants): 1180
ODM variants: 6
Vendor manifests: etc/vintf/manifest_parrot.xml, etc/vintf/manifest_ravelin.xml

## Remaining boot/build blockers

- vendor_boot: stock/common kernel module names differ; validate compiled modules and load order on mist before any boot test
- vendor_dlkm: stock/common kernel module names differ; validate compiled modules and load order on mist before any boot test
- system_dlkm: stock/common kernel module names differ; validate compiled modules and load order on mist before any boot test
- Shared audio and permissions use sku_ravelin: choose actual mist SKU
- Stock mi_ext supplies system/product bind and overlay mounts; plan removal or preservation when writing LineageOS dynamic partitions
- Stock mount table uses AVB chains and encrypted F2FS: validate recovery, vbmeta and first-stage mount behavior
- Select actual active ODM/VINTF/NFC/SIM variant, not all 1180 HAL entries
- Different module lists are not interchangeable without verifying kernel build, ABI, dependencies and module order
- Full vendor ELF/Soong, sepolicy and hardware runtime still need build tests
- The reported WPUMIDC.C11 phone remains unverified against Global WPUMIXM

No bootable/flashable LineageOS build has been created.
