# To do before the first release

- [ ] Logo: design the app logo (the user is working on it), then add it to the release and the installers.
- [ ] Signing: create the Apple "Developer ID Application" and "Developer ID Installer" certificates, and the Windows code-signing certificate. Add the secrets listed in `docs/RELEASE.md`.
- [ ] Signing: run a tagged release once to confirm the Mac and Windows builds sign, notarize and install.
- [ ] Licence: have a lawyer review `LICENSE.txt`, and fill in the year, copyright holder, governing law and contact.
- [ ] Installers: test the `.pkg` on a clean Mac, and the setup `.exe` on a clean Windows machine (install, PATH, uninstall).
- [x] Packaging: "write: Permission denied" warnings from pkgbuild on this Mac are harmless: they go to stderr, the exit code is 0, and the package is complete.
- [ ] App icon: add the Ergaelion icon to the macOS installer (`.icns`) and the Windows installer (`.ico`), and the Start menu and Apps list entries.
- [ ] Git: set up the repository as `NigeleM/Ergaelion` and push with short commit messages.
