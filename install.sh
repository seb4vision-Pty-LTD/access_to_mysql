#!/bin/bash

# Access to MySQL Converter - Installation Script
# This script automates the installation process

echo "=========================================="
echo "Access to MySQL Converter - Setup"
echo "=========================================="
echo ""

# Check Python installation
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Check pip installation
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Installing pip..."
    python3 -m ensurepip --default-pip
fi
echo "✅ pip is available"
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
cd backend
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
cd ..
echo ""

# Check MySQL installation
echo "Checking MySQL installation..."
if command -v mysql &> /dev/null; then
    MYSQL_VERSION=$(mysql --version)
    echo "✅ MySQL found: $MYSQL_VERSION"
else
    echo "⚠️  MySQL not found. Please install MySQL server."
    echo "   Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "   CentOS/RHEL: sudo yum install mysql-server"
    echo "   macOS: brew install mysql"
fi
echo ""

# Check for Access ODBC drivers (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Checking for mdbtools (Access database support)..."
    if command -v mdb-tables &> /dev/null; then
        echo "✅ mdbtools is installed"
    else
        echo "⚠️  mdbtools not found. Installing..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y mdbtools unixodbc unixodbc-dev
        elif command -v yum &> /dev/null; then
            sudo yum install -y mdbtools unixODBC unixODBC-devel
        else
            echo "⚠️  Please install mdbtools manually"
        fi
    fi
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p data/uploads
mkdir -p configs
mkdir -p logs
echo "✅ Directories created"
echo ""

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "Creating .env file..."
    cp backend/.env.example backend/.env
    echo "✅ .env file created (please edit with your settings)"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

# Test backend
echo "Testing backend..."
cd backend
python3 -c "import flask; import pymysql; import pyodbc; import pandas; print('✅ All imports successful')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies verified"
else
    echo "⚠️  Some dependencies may have issues. Check the output above."
fi
cd ..
echo ""

echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your configuration"
echo "2. Start the backend: cd backend && python3 app.py"
echo "3. Open frontend/index.html in your browser"
echo ""
echo "For Windows users:"
echo "- Install Microsoft Access Database Engine 2016 Redistributable"
echo "- Download from: https://www.microsoft.com/en-us/download/details.aspx?id=54920"
echo ""
echo "For detailed instructions, see README.md"
echo ""
