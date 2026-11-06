# Comprehensive stock preflight

The mist one-pass preflight now checks both source-tree structure and hardware facts.
It requires no firmware transfer and uses only the published MD5-verified text reports
plus the pinned shared SM4450 source.

Checks: original kernel module load lists versus common, vendor_boot first-stage fstab,
all eight logical EROFS mount entries, AVB boot chain, F2FS data/metadata encryption,
ODM/vendor VINTF alternatives, and previously verified 995 proprietary source paths.

On success, the workflow publishes compact JSON/Markdown reports to generated/preflight.
Do not equate success with a working ROM; kernel, module, VINTF, AVB and real phone
compatibility still need a complete build and hardware test.
