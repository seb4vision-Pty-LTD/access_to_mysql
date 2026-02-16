# Quick Distribution Guide

## Option 1: Direct Distribution (Quickest)

### For End Users

**Step 1:** Package the app
```bash
# Windows
build.bat 1.0.0

# Linux/macOS
chmod +x build.sh
./build.sh 1.0.0
```

**Step 2:** Upload to GitHub
```bash
# Create release with artifacts
gh release create v1.0.0 --title "Version 1.0.0" \
  -F RELEASE_NOTES.md dist/*
```

**Step 3:** Users download and run
```bash
# Extract
unzip access-to-mysql-converter-v1.0.0.zip

# Run
./run.bat     # Windows
./run.sh      # Linux/macOS
```

---

## Option 2: Docker Distribution (Recommended)

### For Enterprise/Cloud Deployment

**Step 1:** Build and push Docker image
```bash
docker build -t yourdockerhub/access-to-mysql:1.0.0 .
docker tag yourdockerhub/access-to-mysql:1.0.0 yourdockerhub/access-to-mysql:latest
docker push yourdockerhub/access-to-mysql:1.0.0
docker push yourdockerhub/access-to-mysql:latest
```

**Step 2:** Users run Docker
```bash
docker run -p 5000:5000 \
  -v ~/access-uploads:/app/data/uploads \
  yourdockerhub/access-to-mysql:latest
```

**Step 3:** Or use docker-compose
```bash
docker-compose up
```

---

## Option 3: PyPI Distribution (For Developers)

### For pip Installation

**Step 1:** Build distributions
```bash
pip install build twine
python -m build
```

**Step 2:** Upload to PyPI
```bash
twine upload dist/*
```

**Step 3:** Users install via pip
```bash
pip install access-to-mysql-converter
```

---

## Option 4: GitHub Releases (Simplest for GitHub Users)

### Automated via GitHub Actions (Optional)

Create `.github/workflows/release.yml`:
```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install build
      - run: python -m build
      - uses: softprops/action-gh-release@v1
        with:
          files: dist/*
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Then just push a tag:
```bash
git tag v1.0.0
git push origin v1.0.0
```

---

## File Sizes & Formats

| Format | Size | Users | Distribution |
|--------|------|-------|--------------|
| `.zip` | ~50MB | Windows | GitHub Releases |
| `.tar.gz` | ~50MB | Linux/macOS | GitHub Releases |
| `.whl` | ~5MB | Python/Developers | PyPI |
| Docker `tar` | ~300MB | Docker Users | Docker Registry |
| `.exe` (PyInstaller) | ~80MB | Windows Desktop | GitHub Releases |

---

## Recommended Distribution Path

### For Maximum Reach:

1. **GitHub Releases** (Primary)
   - Upload `.zip` and `.tar.gz` files
   - Include sha256 checksums
   - Add installation instructions in release notes

2. **Docker Hub** (Secondary)
   - For teams using containers
   - Point to latest tag
   - Include environment variable docs

3. **PyPI** (Optional)
   - For Python developers
   - Provides `pip install` convenience
   - Requires account setup

---

## Checklist for Each Release

- [ ] Run `RELEASE_CHECKLIST.md` items
- [ ] Update version in `setup.py`
- [ ] Build with `build.bat` or `build.sh`
- [ ] Create GitHub release with artifacts
- [ ] Test downloaded zip/tar.gz with `run.bat`/`run.sh`
- [ ] Optionally push to Docker Hub
- [ ] Optionally publish to PyPI
- [ ] Announce via appropriate channels

---

## File Integrity Verification

**Create checksums:**
```bash
# Windows
certutil -hashfile dist\file.zip SHA256

# Linux/macOS
sha256sum dist/*
```

**Upload:** Include checksums in release notes

**Users verify:**
```bash
sha256sum -c checksums.txt
```

---

## Future Enhancements

- [ ] Windows installer (MSI via WiX)
- [ ] macOS app bundle (DMG)
- [ ] Snap package for Linux
- [ ] Automated changelog generation
- [ ] Version-specific branches for long-term support

---

**Next Release:** After completing this distribution, proceed to `DISTRIBUTION.md` for advanced packaging options.
