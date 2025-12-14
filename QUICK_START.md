# Quick Start - Upload to GitHub & Deploy to Streamlit

## ⚡ Quick Commands (Windows PowerShell)

```powershell
# Navigate to your project
cd d:\Arkan_Almotamer\Automation_add_supplier_number_on_webbeds_from_jood

# Initialize git (if not already done)
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit - WebBeds Automation"

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/Automation_add_supplier_number_on_webbeds_from_jood.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

## 📝 Next Steps

1. **Create GitHub Account**: https://github.com/signup
2. **Create New Repository**: 
   - Go to https://github.com/new
   - Name: `Automation_add_supplier_number_on_webbeds_from_jood`
   - Click "Create repository"
3. **Deploy to Streamlit**:
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your repository and `app.py`
   - Click "Deploy"

## 📁 Files Already Prepared

✅ `.gitignore` - Excludes unnecessary files
✅ `.streamlit/config.toml` - Streamlit configuration
✅ `app.py` - Main application with WebBeds logo
✅ Chrome extension - Unchanged and unaffected

Your app will be live at: `https://automation-webbeds.streamlit.app` (or similar)
