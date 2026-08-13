# Install and start through Python FELLES

Download `eMolPat-<version>-windows.zip` from GitHub Releases. **Code > Download ZIP** contains source code only and cannot install the applications. Optionally verify the ZIP against `eMolPat-<version>-windows.zip.sha256`, then extract the complete archive to a normal local or approved shared folder. Do not move individual wheels between releases.

1. Run **Installer eMolPat.cmd** from the release folder.
2. Ivanti opens Python FELLES (application ID 15694).
3. Paste the copied command with `Ctrl+V`, then press Enter.
4. Wait for the message confirming that eMolPat is installed and verified.
5. Future launches use **Start eMolPat.cmd** with the same paste step.

The installer uses only the extracted `packages`, `wheelhouse`, manifest, and hash lock. Installation is offline and uses `pip --user`. No administrator access is required. If startup fails, contact technical support with `%LOCALAPPDATA%\eMolPat\logs`; never attach patient files.
