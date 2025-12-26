# Quick Upload to GitHub

Run these commands in PowerShell:

```powershell
cd d:\Coding\Fabric

# Configure git (first time only - use your name and email)
git config --global user.name "Husnain Akhtar"
git config --global user.email "husnainakhtar46@example.com"

# Initialize and upload
git init
git add .
git commit -m "Initial commit - Fabric Digital System"
git remote add origin https://github.com/husnainakhtar46/fabric-digital-system.git
git branch -M main
git push -u origin main
```

**Note:** When it asks for password, you'll need a Personal Access Token:
1. Go to GitHub.com
2. Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
3. "Generate new token (classic)"
4. Check "repo" permission
5. Generate and copy the token
6. Use that token as your password when pushing

**Your credentials.json is protected!** It's in .gitignore and won't be uploaded.

After pushing, GitHub will automatically build your APK!
Check the "Actions" tab on your repository.
