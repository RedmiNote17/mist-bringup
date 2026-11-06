# Download-speed investigation

This independent workflow benchmarks Xiaomi CDN endpoints without fetching the 8.1 GB Fastboot archive.

- Tests the *existing* pinned Global fastboot URL and a candidate alternate official Xiaomi domain.
- Also tests a **smaller Global Recovery ROM** (roughly 5 GB), which can supply an OTA payload for later extraction but requires a different inspection pipeline.
- Uses HTTP range requests capped at 8 MiB per candidate; rejects huge unexpected transfers.
- Valid transfers should return HTTP 206 and roughly 8 MiB. Other statuses and errors mean the URL must not be promoted to production.
- Measurements are generated on the Actions runner, not assumed from a mirror listing.
- **Do not switch the full firmware downloader to a mirror until a URL has been confirmed working.**

The previous full-image workflow used up to 12 connections but these may not help when the server/CDN is rate-limited. Short probes isolate this before transferring gigabytes. The existing download workflow is unaffected by this diagnostic addition.

## Verified 8 MiB range measurements (GitHub Actions runner, 7 Nov 2026)

- CDNORG: 12.21 MB/s (primary)
- Singapore Alibaba OSS: 4.15 MB/s (fallback)
- BN: 2.35 MB/s (fallback)

All responded HTTP 206 and returned the requested 8 MiB sample. Full archive checksum still required; small-sample speeds may differ from sustained transfers.
