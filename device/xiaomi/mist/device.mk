# Initial LineageOS 24.0 mist product integration.
# Shared SM4450 tree is pinned in manifests/mist-sm4450.xml.
$(call inherit-product, device/xiaomi/sm4450-common/common.mk)

PRODUCT_SOONG_NAMESPACES += device/xiaomi/mist

# Override common's ravelin-specific device manifest with a mist-named
# subset validated against vendor/etc/vintf/manifest_parrot.xml stock entries.
# Keep the shared Qualcomm audio manifest, but do not merge all stock SKU variants.
DEVICE_MANIFEST_FILE := \
    $(DEVICE_PATH)/configs/vintf/manifest.xml \
    $(AUDIO_HAL_DIR)/configs/parrot/manifest_audio_qti_services.xml

# The common tree expects vendor/xiaomi/sm4450-common/sm4450-common-vendor.mk.
# Generate it using its extract-files.py and vetted stock blobs. This repo's
# docs/verified-global-proprietary-files.txt documents source-presence.
# Do not generate a duplicate vendor/xiaomi/mist module set.

# TODO before first flashable build:
# - Validate this mist VINTF against effective runtime and fix audio SKU / overlays
# - Validate mist mount table, AVB, recovery, kernel module list, SELinux
# - Verify actual WPUMIDC.C11 hardware variant against Global stock
