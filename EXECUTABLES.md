# Fabric Digital System - executables

## ✅ Windows EXE (Admin App)

**Location:** `dist/FabricAdmin.exe` (44 MB)

**How to use:**
1. Copy `FabricAdmin.exe` to any folder
2. Place your `credentials.json` in the same folder
3. Double-click to run

**Features:**
- Enter fabric specifications
- Save to Google Sheets
- Generate QR codes locally

---

## ⚠️ Android APK (Mobile Scanner App)

**Status:** Build configuration ready

**Building the APK requires Linux/WSL.** See: `BUILD_ANDROID_APK.md`

**Quick start (WSL):**
```bash
# In WSL Ubuntu
cd /mnt/d/Coding/Fabric/mobile_app
buildozer android debug
```

**Output:** `mobile_app/bin/FabricScanner-1.0-debug.apk`

---

## System Requirements

### Windows EXE
- Windows 10/11
- Internet connection (for Google Sheets)
- Google service account credentials

### Android APK
- Android 5.0+ (API 21+)
- Camera permission
- Internet connection

---

## Security Note

> [!WARNING]
> **DON'T** distribute APKs with embedded `credentials.json`!
> 
> Service account keys should be kept private. For production use:
> - Use OAuth user authentication instead
> - Or have users provide their own credentials

---

## Build Files

- **Windows:** `build_admin_exe.py` - PyInstaller build script
- **Android:** `mobile_app/buildozer.spec` - Buildozer configuration
- **Guide:** `BUILD_ANDROID_APK.md` - Step-by-step APK build instructions
