# Automatic research publication

The consolidated one-pass firmware research workflow caches extracted images when space is available.

When that workflow succeeds, the independent "Publish successful mist stock inventory to repository" workflow downloads only the text research artifact and commits text reports to generated/stock-global/.

This avoids repeated multi-gigabyte downloads and lets future bring-up work use persistent, version-controlled metadata instead of expired GitHub Actions artifacts.

The two older firmware inspection workflows remain manually runnable but no longer trigger on normal pushes.

A successful stock inventory does not mean the device tree is fully buildable or that the customized WPUMIDC.C11 phone is compatible with Global WPUMIXM images.
