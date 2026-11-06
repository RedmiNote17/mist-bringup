# mist stock vs SM4450 reference proprietary-file paths

Source stock: verified Global `OS3.0.304.0.WPUMIXM`, MD5 `c4450c4e168052ca9de1211306d3beff`.
Reference list: `xiaomi-ravelin/android_device_xiaomi_sm4450-common` at commit `a476fff00d6149fc988f12f43b73cde1587c7b88`, originally derived from Indian `OS3.0.306.0.WPUINXM`.

- **10112** regular-file paths in original EROFS inventory (the inventory missed some files due to traversal/mount-root differences).
- **903** reference paths directly matched the original inventory.
- **92** more reference paths resolved through a read-only mount of the cached stock partitions.
- **995/995** reference source paths now have verified Global-stock location matches.
- **0** reference entries remain unresolved at the path-presence level.

Reports: `generated/stock-global/link-audit/SUMMARY.md` and `stock-link-audit.json`.
Working draft: `device/xiaomi/mist/proprietary-files.txt`.

**Presence alone does not ensure a bootable ROM.** The common tree's source blob-fixup rules, relabeling, runtime dependencies, partition mapping and compatibility with WPUMIDC.C11 remain to be verified.

No full firmware artifact was uploaded: speed testing found CDNORG ~13.5 MB/s in a new bounded range test; the existing verified extracted-partition cache was restored successfully for the audit.
