# Initial LineageOS 24.0 mist product integration.
# Shared SM4450 tree is pinned in manifests/mist-sm4450.xml.
$(call inherit-product, device/xiaomi/sm4450-common/common.mk)

PRODUCT_SOONG_NAMESPACES += device/xiaomi/mist

# The common tree expects vendor/xiaomi/sm4450-common/sm4450-common-vendor.mk.
# Generate it using its extract-files.py and vetted stock blobs. This repo's
# proprietary-files.txt documents source-presence; do not add a duplicate
# vendor/xiaomi/mist module set or commit proprietary ELF binaries.

# TODO before first flashable build:
# - Replace upstream ravelin-specific VINTF / audio SKU / overlays
# - Validate mist mount table, AVB, recovery, kernel module list, SELinux
# - Verify actual WPUMIDC.C11 hardware variant against Global stock
