# Build APK Online with GitHub Actions

No WSL needed! GitHub will build your APK in the cloud for free.

## Setup (One-time, 5 minutes)

### 1. Create GitHub Account
- Go to https://github.com
- Sign up (free)

### 2. Create Repository
- Click "+" → "New repository"
- Name: `fabric-digital-system`
- Public or Private (your choice)
- Click "Create repository"

### 3. Upload Code

**In PowerShell:**
```powershell
cd d:\Coding\Fabric

# Configure git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize
git init
git add .
git commit -m "Initial commit"

# Connect to your GitHub repository
git remote add origin https://github.com/husnainakhtar46/fabric-digital-system.git
git branch -M main
git push -u origin main
```

(It will ask for GitHub username/password - use a Personal Access Token for password)

---

## Build APK (Every time you want a new build)

### Method 1: Automatic (on every code change)
Just push changes:
```powershell
git add .
git commit -m "Update code"
git push
```

APK builds automatically!

### Method 2: Manual Trigger
1. Go to your GitHub repository
2. Click "Actions" tab
3. Click "Build Android APK" workflow
4. Click "Run workflow" → "Run workflow"

---

## Download Your APK

1. **After build completes** (~20-30 minutes first time, ~5 minutes after):
   - Go to "Actions" tab
   - Click on the latest workflow run
   - Scroll down to "Artifacts"
   - Download "FabricScanner-APK"
   - Extract the ZIP file
   - Your APK is inside!

2. **Install on Android:**
   - Send APK to your phone
   - Enable "Install from Unknown Sources"
   - Install the APK

---

## Troubleshooting

**"error: failed to push"**
- Need GitHub Personal Access Token:
  1. GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
  2. Generate new token
  3. Check "repo" permission
  4. Use token as password when pushing

**"Build failed"**
- Check "Actions" tab for error logs
- First build might timeout (free tier has time limits)
- Try again with "Run workflow"

---

## Total Time
- **Setup**: 5-10 minutes
- **First build**: 20-30 minutes
- **Future builds**: 5-10 minutes

Much easier than WSL!
