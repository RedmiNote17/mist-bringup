# Optional lineage-24.0 dependency manifest

The verified LineageOS 24.0 SM4450 common, kernel, module, and devicetree repositories are referenced in `manifests/mist-sm4450.xml`.

In an existing `lineage-24.0` source checkout, review manifest project/path collisions then place the file under `.repo/local_manifests/mist-sm4450.xml` before running `repo sync`.

These projects are borrowed source references and **are not yet validated for the Redmi Note 17 mist device**.

Hardware/xiaomi is a separate LineageOS source dependency. Check if it is already present from the main manifest before adding another local project.

The matching proprietary file list is only a path presence comparison against verified Global stock. Missing symlinks, version differences, AVB, device identity, and SELinux still require resolution.
