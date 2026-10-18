# Releasing Ergaelion

Pushing a tag such as `v1.0.0` runs `.github/workflows/release.yml`. It tests the program, builds it for Linux, macOS (Intel and Apple Silicon) and Windows, signs the macOS and Windows builds when the secrets below are set, and publishes a GitHub release.

## Secrets (Settings → Secrets and variables → Actions)

macOS (needs an Apple Developer Program membership and a "Developer ID Application" certificate):

| Secret | What it is |
| --- | --- |
| `MACOS_CERT_P12` | The certificate and key, exported from Keychain as a `.p12` file, base64-encoded (`base64 -i cert.p12`) |
| `MACOS_CERT_PASSWORD` | The password chosen when exporting the `.p12` |
| `MACOS_SIGN_IDENTITY` | The identity name, e.g. `Developer ID Application: Your Name (TEAMID)` |
| `APPLE_ID` | The Apple ID used for notarization |
| `APPLE_APP_PASSWORD` | An app-specific password for that Apple ID |
| `APPLE_TEAM_ID` | The 10-character team ID |
| `MACOS_INSTALLER_IDENTITY` | The installer identity, e.g. `Developer ID Installer: Your Name (TEAMID)`. Needs a second certificate of that kind, exported the same way as above and added to the `.p12` |

Windows (needs a code-signing certificate, from a certificate authority):

| Secret | What it is |
| --- | --- |
| `WINDOWS_PFX_BASE64` | The `.pfx` certificate, base64-encoded |
| `WINDOWS_PFX_PASSWORD` | The password for the `.pfx` |

If a secret is missing, that platform's build is published unsigned, and the release notes still work.

## Before the first release

- Run `make test` locally (or push a branch and run the workflow with "Run workflow").
- Check the version in `goplaybook/main.go` and `gtplaybook/__init__.py` matches the tag.

## Installers

- `Ergaelion-<version>-macos.pkg` shows the licence, then installs `Ergaelion` to `/usr/local/bin`. It is signed with the Developer ID Installer identity and notarized, when those secrets are set.
- `Ergaelion-<version>-windows-setup.exe` shows the licence, installs to Program Files, and can add the program to the PATH. It is signed when the Windows secrets are set.

The installers include `LICENSE.txt`. Review the licence with a lawyer before the first public release.
