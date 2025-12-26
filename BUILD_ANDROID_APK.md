# Building Android APK for Fabric Scanner

## Prerequisites

Android APK builds using Buildozer require a **Linux environment**. Choose one:

### Option 1: WSL (Windows Subsystem for Linux) - Recommended

1. **Install WSL Ubuntu:**
   ```powershell
   wsl --install -d Ubuntu
   ```

2. **Access your Fabric project in WSL:**
   ```bash
   cd /mnt/d/Coding/Fabric/mobile_app
   ```

3. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinyxml-dev libffi-dev libssl-dev
   pip3 install --user buildozer cython==0.29.33
   ```

4. **Build APK:**
   ```bash
   buildozer android debug
   ```

   **First build takes 30-60 minutes** (downloads Android SDK/NDK ~2GB)
   **Subsequent builds:** 5-10 minutes

5. **Get APK:**
   - Located at: `mobile_app/bin/FabricScanner-1.0-arm64-v8a-debug.apk`
   - Copy to Windows: `cp bin/*.apk /mnt/d/Coding/Fabric/`

### Option 2: Native Linux

If you have a Linux machine:

```bash
cd /path/to/Fabric/mobile_app
sudo apt install buildozer
buildozer android debug
```

### Option 3: Cloud Build (GitHub Actions)

Create `.github/workflows/build-apk.yml`:

```yaml
name: Build APK
on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build with Buildozer
        uses: ArtemSBulgakov/buildozer-action@v1
        with:
          workdir: mobile_app
          buildozer_version: stable
      - name: Upload APK
        uses: actions/upload-artifact@v2
        with:
          name: FabricScanner
          path: mobile_app/bin/*.apk
```

## Important Notes

### Credentials

- **DON'T** include `credentials.json` in the APK (security risk!)
- Instead:
  1. Use environment variables, OR
  2. Have users add their own credentials after install, OR
  3. Use OAuth user authentication instead of service account

### Camera Permissions

The `buildozer.spec` already includes `CAMERA` permission. On first run, Android will prompt the user to allow camera access.

### Testing

APK will be a **debug build** (unsigned). For production:
```bash
buildozer android release
# Then sign with keystore
```

## Troubleshooting

**Build fails?**
- Check Java version: `java -version` (need 17+)
- Clear cache: `buildozer android clean`
- Check logs in `.buildozer/logs/`

**APK won't install?**
- Enable "Install from Unknown Sources" in Android settings
- For production, need signed release build

## Next Steps

1. Build APK using one of the options above
2. Install on Android device
3. Allow camera permissions when prompted
4. Scan QR codes!
