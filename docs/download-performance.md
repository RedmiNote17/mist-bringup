# Download-speed investigation

This independent workflow benchmarks Xiaomi CDN endpoints without fetching the 8.1 GB Fastboot archive.

- Tests the *existing* pinned Global fastboot URL and a candidate alternate official Xiaomi domain.
- Also tests a **smaller Global Recovery ROM** (roughly 5 GB), which can supply an OTA payload for later extraction but requires a different inspection pipeline.
- Uses HTTP range requests capped at 8 MiB per candidate; rejects huge unexpected transfers.
- Valid transfers should return HTTP 206 and roughly 8 MiB. Other statuses and errors mean the URL must not be promoted to production.
- Measurements are generated on the Actions runner, not assumed from a mirror listing.
- **Do not switch the full firmware downloader to a mirror until a URL has been confirmed working.**

The previous full-image workflow used up to 12 connections but these may not help when the server/CDN is rate-limited. Short probes isolate this before transferring gigabytes. The existing download workflow is unaffected by this diagnostic addition.
