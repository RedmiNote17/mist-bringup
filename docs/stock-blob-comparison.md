# mist Global vs existing SM4450 common proprietary list

Reference: https://github.com/xiaomi-ravelin/android_device_xiaomi_sm4450-common/tree/lineage-24.0

- Verified stock: **OS3.0.304.0.WPUMIXM** (Global), 10,112 regular-file paths.
- Reference list originally based on **OS3.0.306.0.WPUINXM** (India).
- Compared source paths in the reference proprietary-files entries, ignoring extraction destination and fixup flags.
- **903** entries have matching regular-file source paths.
- **92** entries were not observed as regular files in the inventory.

**Important:** Missing from the inventory does not prove absent from the stock image: symbolic links were excluded by the first-stage scanner. Some references may also be region-specific or target a different build.

`device/xiaomi/mist/proprietary-files.txt` contains the matching subset as a reviewable draft; it is not an established, boot-tested proprietary list.
`docs/stock-blob-unresolved.txt` records non-matching paths for follow-up symlink and version checks.

Don't add Indian build binaries to the Global tree without file-by-file compatibility verification. No firmware binary is redistributed.
