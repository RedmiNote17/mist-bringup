# Consolidated mist bring-up: one download

Preferred workflow: .github/workflows/full-bringup.yml.

Instead of rerunning separate stock extraction jobs, this workflow:

1. Performs fast offline tests and installs prerequisites before downloading.
2. Measures official Xiaomi CDN candidates with 8 MiB ranges and selects the fastest valid response.
3. Downloads the pinned Global Fastboot archive once, validates complete MD5, extracts selected boot images and eight EROFS logical partitions.
4. Caches roughly 7 GiB of verified extracted partition images when Actions cache quota permits so future fixes can reuse them.
5. Inventories all files, potential proprietary blobs, read-only system properties, VINTF, HAL, kernel modules, fstab, init and boot ramdisk configs.
6. Uploads metadata-only reports, not a ROM or proprietary binary images.

## Limitations

- An actual bootable LineageOS device/vendor/kernel configuration is still pending.
- WPUMIXM Global is a research reference, not equivalent to owner's earlier WPUMIDC.C11.
- Benchmark throughput varies and does not guarantee the maximum download rate.
- Cache entries can be evicted or refused by quota; cache misses require a single fresh download.
- The stock image metadata should be reviewed before applying settings to BoardConfig and proprietary-files.txt.
- Older one-shot inspection workflows are retained for manual use but this is the preferred consolidated pipeline.
