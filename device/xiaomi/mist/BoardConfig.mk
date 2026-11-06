# Initial mist device BoardConfig: only values verified from
# Xiaomi OS3.0.304.0.WPUMIXM stock fastboot headers and rawprogram XML.
# This is NOT a complete, bootable LineageOS device tree.
DEVICE_PATH := device/xiaomi/mist

TARGET_ARCH := arm64
TARGET_ARCH_VARIANT := armv8-a
TARGET_CPU_ABI := arm64-v8a

# Qualcomm SM4450 / Parrot confirmed by mist-w-oss and stock module directories.
TARGET_BOARD_PLATFORM := parrot
BOARD_USES_QCOM_HARDWARE := true
TARGET_KERNEL_VERSION := 6.6

# Source in verified Global stock includes a standalone DTBO partition.
BOARD_DTBOIMG_PARTITION_SIZE := 25165824

# Observed on stock boot, vendor_boot, init_boot and recovery headers.
BOARD_BOOTIMG_HEADER_VERSION := 4
BOARD_MKBOOTIMG_ARGS += --header_version 4
BOARD_BOOTIMAGE_PARTITION_SIZE := 100663296
BOARD_VENDOR_BOOTIMAGE_PARTITION_SIZE := 100663296
BOARD_INIT_BOOT_IMAGE_PARTITION_SIZE := 8388608
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 104857600

# rawprogram0.xml: super, 2490368 sectors of 4096 bytes.
BOARD_SUPER_PARTITION_SIZE := 10200547328

# Still TODO: TARGET_BOARD_PLATFORM, kernel/DTBO integration, mount table,
# dynamic group allocation, vendor dependencies, VINTF, SEPolicy,
# verified AVB settings, and all A/B update details.
