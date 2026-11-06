# device/xiaomi/mist — preliminary LineageOS 24.0 tree

BoardConfig.mk inherits the pinned SM4450 common BoardConfig and overrides the verified mist super, boot,
vendor_boot, init_boot, recovery, and DTBO sizes. Super size is set BEFORE common inclusion to prevent
improper immediate evaluation of the dynamic group size.

device.mk inherits the SM4450 common product, which in turn expects vendor/xiaomi/sm4450-common.
The 995-path proprietary-files.txt is evidence checked against Global stock; it is NOT an extracted vendor tree.
Do not run a separate mist extraction that duplicates common vendor modules.

**Not ready for full ROM building or flashing:** upstream common still uses ravelin SKU audio and VINTF;
mist-specific first-stage mount/AVB/SEPolicy, actual vendor extraction, kernel and runtime hardware tests remain.

Run the single GH Actions mist-preflight workflow, then inspect its explicit list of remaining blockers.

## Corrections

- The device-specific VINTF source at `configs/vintf/manifest.xml` replaces
  the generic tree's ravelin-specific manifest source; entries are matched
  against published stock HAL evidence.
- `proprietary-files.txt` contains no duplicate common blob entries.
  The verified 995-path reference moved to `docs/verified-global-proprietary-files.txt`.
- Use `extract-files.py` after syncing the pinned common tree; it delegates
  to upstream extraction/fixups instead of generating a second vendor module set.
- Common audio still uses sku_ravelin paths, and shared first-stage fstab still
  needs reconciliation with stock F2FS/encryption. Neither is declared solved.
