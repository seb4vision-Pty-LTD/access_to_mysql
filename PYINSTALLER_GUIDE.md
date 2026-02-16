# PyInstaller Windows EXE Build Guide

## Prerequisites

```powershell
pip install pyinstaller
```

## Build Methods

### Method 1: Using Spec File (Recommended)

```powershell
pyinstaller AccessToMySQL.spec
```

Output: `dist/AccessToMySQL.exe`

### Method 2: Direct Command

```powershell
pyinstaller `
  --onefile `
  --name "AccessToMySQL" `
  --console `
  --add-data "frontend:frontend" `
  --add-data "backend:backend" `
  --hidden-import=flask `
  --hidden-import=flask_cors `
  --hidden-import=pymysql `
  --hidden-import=pyodbc `
  --hidden-import=pandas `
  --hidden-import=sqlalchemy `
  backend/app.py
```

## Build Output

```
dist/
  └── AccessToMySQL.exe      (Standalone executable ~150MB)
build/
  └── AccessToMySQL/         (Temporary build files)
AccessToMySQL.spec            (Build configuration)
```

## Running the EXE

```powershell
.\dist\AccessToMySQL.exe
```

The app will:
1. Extract to temporary directory (Windows AppData\Local\Temp\_MEI*)
2. Create data/uploads, logs, configs folders
3. Start Flask server on http://localhost:5000
4. Open in browser automatically (optional)

## ⚠️ Antivirus Warning

PyInstaller-bundled executables may trigger antivirus warnings (false positive). To reduce this:

1. **Whitelist** the exe in your antivirus
2. **Sign** the exe with a code signing certificate (enterprise)
3. **Use installer** (MSI) instead of standalone exe

## Troubleshooting

### "Frontend not found" Error

If you see `Error serving index.html: [Errno 2] No such file or directory`:

1. Verify frontend folder exists in project
2. Rebuild: `pyinstaller AccessToMySQL.spec --distpath dist --workpath build --specpath .`
3. Check console output for base path during startup

### EXE Won't Start

1. Run from command line to see error messages:
   ```powershell
   .\dist\AccessToMySQL.exe 2>&1 | more
   ```

2. Check Windows Event Viewer for crash details

3. Ensure all DLL dependencies are included (rare)

### Port 5000 Already in Use

Change the port in `backend/app.py` line:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)  # Changed to 5001
```

Then rebuild the EXE.

## Optimization

### Reduce EXE Size

```powershell
# Remove debug symbols
pyinstaller AccessToMySQL.spec --distpath dist --build-folder build

# Remove unnecessary modules
# Edit AccessToMySQL.spec and add to excludedimports list
```

### Faster Startup

1. Use `--onedir` instead of `--onefile` (dirs load faster)
2. Remove `--debug` flag
3. Use UPX compression (if installed)

## Distribution

### Step 1: Create Installer (Optional)

```powershell
# Using NSIS (more pro-looking)
makensis /DPRODUCT_VERSION=1.0.0 installer.nsi
```

### Step 2: Package for Distribution

```powershell
# Create zip
Compress-Archive -Path dist\AccessToMySQL.exe -DestinationPath AccessToMySQL-1.0.0.zip

# Calculate checksum
(Get-FileHash dist\AccessToMySQL.exe).Hash | Out-File checksums.txt
```

### Step 3: Upload

Upload to GitHub, distribute link to users.

### Users Run It

```powershell
# Extract zip
Expand-Archive AccessToMySQL-1.0.0.zip

# Run
.\AccessToMySQL.exe

# Opens http://localhost:5000 automatically
```

## Auto-Open Browser (Optional)

To automatically open the browser when EXE starts, add to `backend/app.py`:

```python
import webbrowser

if __name__ == '__main__':
    webbrowser.open('http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
```

Then rebuild EXE.

## CI/CD Integration

### GitHub Actions (Auto-build on Release)

Create `.github/workflows/build-exe.yml`:

```yaml
name: Build Windows EXE

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r backend/requirements.txt pyinstaller
      - run: pyinstaller AccessToMySQL.spec
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/AccessToMySQL.exe
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Then:
```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions auto-builds and creates release with EXE.

## Support Files to Include

In the same folder as `AccessToMySQL.exe`, place:
- `README.txt` (quick start instructions)
- `LICENSE.txt` (MIT license)
- `REQUIREMENTS.txt` (system requirements)

Users just need to:
1. Download `AccessToMySQL.exe`
2. Double-click to run
3. Open `http://localhost:5000` in browser
4. Done!

---

## Command Reference

| Command | Purpose |
|---------|---------|
| `pyinstaller AccessToMySQL.spec` | Build using spec file |
| `pyinstaller --info-imports backend/app.py` | List all imports |
| `pyinstaller --onedir backend/app.py` | One-folder exe (faster) |
| `pyinstaller --windowed backend/app.py` | Hide console window |
| `pyinstaller --clean` | Clean build cache |

---

**Built with PyInstaller v6.0+**
