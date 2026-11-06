# Preliminary product skeleton. NOT ready to compile or boot.
$(call inherit-product, device/xiaomi/mist/device.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

PRODUCT_NAME := lineage_mist
PRODUCT_DEVICE := mist
PRODUCT_BRAND := Redmi
PRODUCT_MANUFACTURER := Xiaomi
PRODUCT_MODEL := Redmi Note 17 5G
