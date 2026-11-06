# Redmi Note 17 5G (mist) — stock fastboot observations

All sizes below are from the verified OS3.0.304.0.WPUMIXM fastboot package, not
from generated recovery-tree guesses.

| Partition | Confirmed bytes | Source |
| --- | ---: | --- |
| boot | 100663296 | rawprogram4.xml and boot.img |
| vendor_boot | 100663296 | rawprogram4.xml and vendor_boot.img |
| init_boot | 8388608 | stock image |
| recovery | 104857600 | stock image |
| super | 10200547328 | rawprogram0.xml: 2490368 sectors × 4096 B |
| dtbo | 25165824 | stock image |
| metadata | 67108864 | rawprogram0.xml and Android sparse header |

Stock Android boot images have header **v4** for boot, vendor_boot, init_boot,
and recovery. The archive verified with MD5 `c4450c4e168052ca9de1211306d3beff`.

The previously discovered auto-generated TWRP tree uses a **different**
hardcoded super size. Do not copy its full BoardConfig into LineageOS.

Next-stage workflow: [inspect-partitions.yml](../../.github/workflows/inspect-partitions.yml)
downloads the verified source, extracts `super.img` and boot-related headers,
enumerates logical partitions and detects EROFS/ext4/F2FS signatures. Artifacts
are metadata-only; no copyrighted/proprietary firmware image is redistributed.

The owner's WPUMIDC.C11 firmware variant still needs separate validation.
