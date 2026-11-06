# Redmi Note 17 5G (mist), preliminary LineageOS 24.0 board configuration.
# Stock evidence: OS3.0.304.0.WPUMIXM (MD5 c4450c4e168052ca9de1211306d3beff).
# NOT FLASH/BOOT VALIDATED. Variant WPUMIDC.C11 has not been checked.
DEVICE_PATH := device/xiaomi/mist

# Must be defined BEFORE including the common config: the common file uses
# immediately expanded := expressions to compute the dynamic group size.
BOARD_SUPER_PARTITION_SIZE := 10200547328

# Qualcomm parrot/SM4450 shared kernel, modules, QCOM HAL and sepolicy configuration.
include device/xiaomi/sm4450-common/BoardConfigCommon.mk

# Override common-device values with verified mist stock partition sizes.
BOARD_BOOT_HEADER_VERSION := 4
BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 100663296
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 104857600
BOARD_DTBOIMG_PARTITION_SIZE := 25165824

# Same 4 MiB overhead convention as the shared common tree, with a stock
# 10,200,547,328-byte super partition. mi_ext is stock-only and is not included
# in the LineageOS dynamic partition group until its removal/layout is reviewed.
BOARD_QTI_DYNAMIC_PARTITIONS_SIZE := 10196353024

# Do not import ravelin-specific VINTF, SKU or kernel-module assumptions blindly.
# The common tree has manifest_ravelin.xml and sku_ravelin audio settings.
# Preflight reports these as open device-specific blockers; no release is safe yet.
