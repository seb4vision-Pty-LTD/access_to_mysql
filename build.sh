#!/bin/bash
# Build script for creating distribution packages
# Usage: ./build.sh [version]

set -e

if [ -z "$1" ]; then
    echo "Usage: ./build.sh [version]"
    echo "Example: ./build.sh 1.0.0"
    exit 1
fi

VERSION=$1

echo ""
echo "========================================"
echo "Building Access to MySQL Converter v$VERSION"
echo "========================================"
echo ""

# Activate venv
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install build tools
echo "Installing build tools..."
pip install --upgrade pip setuptools wheel build twine

# Clean old builds
echo "Cleaning old builds..."
rm -rf dist build *.egg-info

# Update version in setup.py
echo "Updating version to $VERSION..."
sed -i "s/version='[^']*'/version='$VERSION'/" setup.py

# Build distributions
echo ""
echo "Building source and wheel distributions..."
python -m build

# List output
echo ""
echo "========================================"
echo "Build complete! Distribution files:"
echo "========================================"
ls -lh dist/

echo ""
echo "Next steps:"
echo "1. Test with: pip install dist/access-to-mysql-converter-$VERSION-py3-none-any.whl"
echo "2. Upload to GitHub: gh release create v$VERSION dist/*"
echo "3. Upload to PyPI: twine upload dist/*"
echo ""
