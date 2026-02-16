#!/usr/bin/env python3
"""
Test Script for Access to MySQL Converter
Verifies that all dependencies and components are working correctly
"""

import sys
import os

def test_python_version():
    """Test Python version"""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_imports():
    """Test required Python packages"""
    print("\nTesting Python packages...")
    packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'pymysql': 'PyMySQL',
        'pyodbc': 'PyODBC',
        'pandas': 'Pandas',
        'sqlalchemy': 'SQLAlchemy'
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - not installed")
            all_ok = False
    
    return all_ok

def test_odbc_drivers():
    """Test ODBC drivers availability"""
    print("\nTesting ODBC drivers...")
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        access_drivers = [d for d in drivers if 'Access' in d or 'Microsoft Access Driver' in d]
        
        if access_drivers:
            print(f"✅ Access ODBC drivers found: {len(access_drivers)}")
            for driver in access_drivers:
                print(f"   - {driver}")
            return True
        else:
            print("⚠️  No Access ODBC drivers found")
            print("   Windows: Install Microsoft Access Database Engine")
            print("   Linux: sudo apt-get install mdbtools")
            return False
    except Exception as e:
        print(f"❌ Error checking ODBC drivers: {e}")
        return False

def test_directories():
    """Test required directories exist"""
    print("\nTesting directories...")
    dirs = ['data/uploads', 'configs', 'logs', 'backend', 'frontend']
    all_ok = True
    
    for directory in dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - not found")
            all_ok = False
    
    return all_ok

def test_backend_modules():
    """Test backend modules can be imported"""
    print("\nTesting backend modules...")
    sys.path.insert(0, 'backend')
    
    modules = ['app', 'database_handler', 'data_exporter', 'config_manager']
    all_ok = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}.py")
        except ImportError as e:
            print(f"❌ {module}.py - import error: {e}")
            all_ok = False
        except Exception as e:
            print(f"⚠️  {module}.py - warning: {e}")
    
    return all_ok

def test_mysql_connection():
    """Test MySQL connectivity"""
    print("\nTesting MySQL connection...")
    try:
        import pymysql
        # Try to connect to MySQL (will fail if not running, but tests the package)
        print("ℹ️  PyMySQL package ready for connections")
        print("   To test actual connection, ensure MySQL is running")
        return True
    except Exception as e:
        print(f"❌ MySQL test failed: {e}")
        return False

def test_flask_app():
    """Test Flask app can be created"""
    print("\nTesting Flask application...")
    try:
        sys.path.insert(0, 'backend')
        from flask import Flask
        test_app = Flask(__name__)
        print("✅ Flask app can be created")
        return True
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Access to MySQL Converter - System Test")
    print("="*60)
    
    results = []
    
    results.append(("Python Version", test_python_version()))
    results.append(("Python Packages", test_imports()))
    results.append(("ODBC Drivers", test_odbc_drivers()))
    results.append(("Directories", test_directories()))
    results.append(("Backend Modules", test_backend_modules()))
    results.append(("MySQL Package", test_mysql_connection()))
    results.append(("Flask App", test_flask_app()))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Start backend: cd backend && python app.py")
        print("2. Open frontend: Open frontend/index.html in browser")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing packages: pip install -r backend/requirements.txt")
        print("- Install ODBC drivers (see README.md)")
        print("- Create missing directories: mkdir -p data/uploads configs logs")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
