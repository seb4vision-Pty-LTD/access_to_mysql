# Distribution & Packaging Guide

## Creating Distribution Packages

This document explains how to package and distribute the Access to MySQL Converter application.

---

## 1. Source Distribution (Easiest)

### For GitHub Release

```bash
# Create a clean distribution archive
git clone https://github.com/yourusername/access-to-mysql-converter.git
cd access-to-mysql-converter
git tag v1.0.0
git push origin v1.0.0

# Create zip for distribution
7z a -r access-to-mysql-converter-v1.0.0.zip . `
  -xr!"*.git" -xr!".venv" -xr!"data/uploads/*" -xr!"logs/*"

# Or on Linux/Mac
zip -r access-to-mysql-converter-v1.0.0.zip . \
  -x ".git/*" ".venv/*" "data/uploads/*" "logs/*" "__pycache__/*" "*.pyc"
```

### Release Distribution Steps

1. **Clean build**
   ```bash
   pip install --upgrade build wheel
   python -m build
   ```

2. **Output files**
   ```
   dist/
   ├── access-to-mysql-converter-1.0.0.tar.gz   # Source
   └── access-to-mysql-converter-1.0.0-py3-none-any.whl  # Wheel
   ```

3. **Upload to PyPI (Optional)**
   ```bash
   pip install twine
   twine upload dist/*
   ```

4. **Then users can install via**
   ```bash
   pip install access-to-mysql-converter
   ```

---

## 2. Docker Distribution (Recommended for Enterprise)

### Build Docker Image

```bash
# Build
docker build -t access-to-mysql:1.0.0 .
docker tag access-to-mysql:1.0.0 yourdockerhub/access-to-mysql:latest

# Push to registry
docker push yourdockerhub/access-to-mysql:latest
```

### Docker Deployment

Users simply run:
```bash
docker run -p 5000:5000 \
  -v ~/access-uploads:/app/data/uploads \
  yourdockerhub/access-to-mysql:latest
```

---

## 3. Executable (Windows EXE)

### Using PyInstaller

```bash
pip install pyinstaller

# Create exe
pyinstaller --onefile \
  --name "AccessToMySQLConverter" \
  --windowed \
  --add-data "frontend:frontend" \
  --icon icon.ico \
  backend/app.py
```

Output: `dist/AccessToMySQLConverter.exe`

---

## 4. Installer (Windows MSI)

### Using WiX Toolset

```bash
# Create wxs template
heat.exe dir frontend -cg WebFiles -o Files.wxs

# Compile and link
candle.exe Product.wxs Files.wxs -o obj\
light.exe obj\*.wixobj -o AccessToMySQLConverter-1.0.0.msi
```

---

## 5. Release Checklist

Before releasing:

- [ ] Update version in `setup.py`
- [ ] Update version in `backend/requirements.txt` (if changed)
- [ ] Update `README_DISTRIBUTION.md` with new features
- [ ] Run tests: `pytest backend/`
- [ ] Clean build artifacts: `rm -rf build/ dist/ *.egg-info`
- [ ] Test installation: `pip install -e .`
- [ ] Verify startup scripts work
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Build distributions
- [ ] Create GitHub release with archives
- [ ] Update documentation links

---

## 6. Installation Methods for Users

### Method A: Startup Script (Easiest - Recommended)

```bash
# Windows
run.bat

# Linux/Mac
./run.sh
```

### Method B: Direct Python

```bash
pip install -r backend/requirements.txt
python backend/app.py
```

### Method C: Docker

```bash
docker-compose up
```

### Method D: PyPI Package

```bash
pip install access-to-mysql-converter
access-to-mysql
```

### Method E: Windows Executable (Future)

```
AccessToMySQLConverter.exe
```

---

## 7. System Requirements by Distribution

| Method | Requirements | Target Users |
|--------|--------------|--------------|
| Startup Script | Python 3.9+ | Developers, Technical Users |
| Docker | Docker Engine | DevOps, Sysadmins |
| PyPI | Python 3.9+ | Python Users |
| Windows EXE | Windows Only | End Users |
| Windows MSI | Windows Only | Enterprise IT |

---

## 8. Versioning Strategy

```
1.0.0
│ │ └─ Patch (bug fixes)
│ └─── Minor (features, backward compatible)
└───── Major (breaking changes)
```

### Version Bumping

```bash
# Patch
bumpversion patch

# Minor
bumpversion minor

# Major
bumpversion major
```

---

## 9. Upload Locations

### Public Repositories
- **GitHub:** https://github.com/yourusername/access-to-mysql-converter/releases
- **PyPI:** https://pypi.org/project/access-to-mysql-converter/
- **Docker Hub:** https://hub.docker.com/r/yourusername/access-to-mysql

### Private/Enterprise
- Corporate artifact repository
- Internal file server
- OnPremise Docker registry
- Windows domain distribution

---

## 10. Documentation Distribution

Include in every release:

```
/docs/
  ├── README_DISTRIBUTION.md
  ├── SETUP-GUIDE.md
  ├── DEPLOYMENT_SUMMARY.md
  ├── PROJECT_STRUCTURE.md
  └── QUICKSTART.md
```

---

## 11. Security for Distribution

- Sign releases with GPG
- Provide SHA256 checksums
- Use HTTPS for downloads
- Scan for vulnerabilities before release
- Include security policy in README

---

## 12. Update/Upgrade Path

### For Pip Users
```bash
pip install --upgrade access-to-mysql-converter
```

### For Docker Users
```bash
docker pull yourdockerhub/access-to-mysql:latest
docker-compose up
```

### For Startup Users
```bash
git pull origin main
./run.bat  # or run.sh
```

---

## Example: Complete Release Workflow

```bash
# 1. Update version
sed -i 's/"1.0.0"/"1.0.1"/' setup.py

# 2. Commit
git add setup.py
git commit -m "Release v1.0.1"

# 3. Tag
git tag v1.0.1
git push origin main
git push origin v1.0.1

# 4. Build distributions
pip install build
python -m build

# 5. Create GitHub release
gh release create v1.0.1 --title "Version 1.0.1" \
  --notes "Bug fixes and improvements"

# 6. Upload artifacts to release
gh release upload v1.0.1 dist/*

# 7. Optional: Upload to PyPI
twine upload dist/*

# 8. Optional: Upload to Docker Hub
docker build -t yourhub/access-to-mysql:1.0.1 .
docker push yourhub/access-to-mysql:1.0.1
```

---

**For support on packaging, refer to:**
- Python Packaging Guide: https://packaging.python.org
- setuptools Documentation: https://setuptools.pypa.io
- PyPI Project Creation: https://packaging.python.org/tutorials/packaging-projects/
