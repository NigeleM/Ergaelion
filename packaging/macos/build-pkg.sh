#!/usr/bin/env bash
# Builds Ergaelion-<version>-macos.pkg: an installer that shows the licence, then installs
# Ergaelion to /usr/local/bin and the licence to /usr/local/share/ergaelion. The folders that
# already exist (/usr/local) keep their ownership.
#
#   packaging/macos/build-pkg.sh <version> <amd64 binary> <arm64 binary> <output dir> <licence file>
#
# The two binaries are combined into one universal file. The installer is signed with a
# Developer ID Installer identity only when MACOS_INSTALLER_IDENTITY is set.
set -euo pipefail

VERSION="$1"
AMD64="$2"
ARM64="$3"
OUT="$4"
LICENCE="$5"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$WORK/payload/bin" "$WORK/payload/share/ergaelion" "$WORK/resources" "$WORK/packages" "$OUT"
lipo -create "$AMD64" "$ARM64" -output "$WORK/payload/bin/Ergaelion"
chmod 755 "$WORK/payload/bin/Ergaelion"
cp "$LICENCE" "$WORK/payload/share/ergaelion/LICENSE.txt"
cp "$LICENCE" "$WORK/resources/LICENSE.txt"

pkgbuild --root "$WORK/payload" --identifier "com.nigelm.ergaelion" --version "$VERSION" \
  --install-location /usr/local --ownership recommended "$WORK/packages/ergaelion-component.pkg"

cat > "$WORK/distribution.xml" <<XML
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
  <title>Ergaelion</title>
  <license file="LICENSE.txt" mime-type="text/plain"/>
  <options customize="never" require-scripts="false" hostArchitectures="x86_64,arm64"/>
  <choices-outline><line choice="default"/></choices-outline>
  <choice id="default" title="Ergaelion"><pkg-ref id="com.nigelm.ergaelion"/></choice>
  <pkg-ref id="com.nigelm.ergaelion" version="$VERSION" onConclusion="none">ergaelion-component.pkg</pkg-ref>
</installer-gui-script>
XML

PKG="$OUT/Ergaelion-$VERSION-macos.pkg"
ARGS=(--distribution "$WORK/distribution.xml" --resources "$WORK/resources" --package-path "$WORK/packages")
if [ -n "${MACOS_INSTALLER_IDENTITY:-}" ]; then
  ARGS+=(--sign "$MACOS_INSTALLER_IDENTITY")
fi
productbuild "${ARGS[@]}" "$PKG"
echo "built $PKG"
