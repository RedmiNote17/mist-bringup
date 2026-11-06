# Redmi Note 17 5G (mist) — unofficial LineageOS 24.0 bring-up

**Status: research-backed device-tree scaffold, NOT a flashable or boot-tested ROM.**

Repository: RedmiNote17/mist-bringup. Target: Android 17 / LineageOS 24.0.

## Most recent verified stock baseline

- Xiaomi Global OS3.0.304.0.WPUMIXM (Android 16), MD5 c4450c4e168052ca9de1211306d3beff.
- Eight EROFS logical partitions in 10,200,547,328-byte super.
- Boot header v4; kernel source baseline Linux 6.6; 460 recorded .ko modules.
- 995 source paths cross-checked with the SM4450 common proprietary list.
- Stock inventory and reconciled paths are versioned in generated/stock-global.

## One-run integration workflow

GitHub Actions: mist one-pass LineageOS 24.0 preflight (no firmware download).

This single run validates all Python and tree tests, pulls only the pinned SM4450 common-tree source, verifies
device/product/BoardConfig inheritance, stock partition size/order, module counts, VINTF metadata,
and all 995 proprietary source paths. It uploads a small report describing remaining boot blockers.

The shared SM4450 kernel/modules/devicetree dependencies are pinned in manifests/mist-sm4450.xml.
BoardConfig and device.mk inherit the common SM4450 configuration but are not release-ready:
the common project includes ravelin-specific audio and VINTF assumptions requiring mist adaptation.

## Download/caching policy

Do not upload the full ~8.1 GB firmware. Measured official CDNORG speeds: ~13 MB/s on GitHub runners.
One-pass source analysis succeeded and its extracted partition cache was restored and reused.
Stock research can be inspected without another firmware download; older download workflows are manually invoked.

## Device safety

Stock image WPUMIXM is NOT necessarily compatible with the owner's previously reported WPUMIDC.C11 variant.
AVB, VINTF, recovery, kernel and real-device tests are blockers before any flashable release.
See docs/current-bringup-status.md and docs/sm4450-common-analysis.md.

## Proprietary blob ownership and device VINTF

The shared SM4450 common tree owns the 995 device-common proprietary paths and
its extractor applies crucial upstream blob/ELF fixups. The original cross-checked
path list now lives in `docs/verified-global-proprietary-files.txt`, **not** as a
second `vendor/xiaomi/mist` extraction list.

`device/xiaomi/mist/extract-files.py` forwards extraction commands to
`device/xiaomi/sm4450-common/extract-files.py` inside an initialized LineageOS
checkout. It does not download or publish proprietary binaries on GitHub.

The `mist` device VINTF override contains only Gatekeeper, DRM/WFD-HDCP,
and WFD session instances confirmed in stock `manifest_parrot.xml`. This
removes the ravelin-specific manifest input but does **not** prove hardware
services work until the exact device variant is tested.
