"""
Master Creator MVP - Setup Verification Script
Checks if all dependencies and configuration are correct
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python version {version.major}.{version.minor} is too old (need 3.10+)")
        return False


def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name

    try:
        __import__(import_name)
        print(f"✓ {package_name} installed")
        return True
    except ImportError:
        print(f"✗ {package_name} not installed")
        return False


def check_env_file():
    """Check if .env file exists and has API key"""
    env_path = Path(".env")

    if not env_path.exists():
        print("✗ .env file not found")
        return False

    print("✓ .env file exists")

    # Check if API key is configured
    with open(env_path, 'r') as f:
        content = f.read()

    if "your_anthropic_api_key_here" in content:
        print("  ⚠ Warning: API key not configured in .env file")
        return False
    elif "ANTHROPIC_API_KEY=" in content:
        print("  ✓ API key configured")
        return True
    else:
        print("  ✗ ANTHROPIC_API_KEY not found in .env")
        return False


def check_directories():
    """Check if required directories exist"""
    required_dirs = ["src", "data", "tests"]
    all_exist = True

    for dirname in required_dirs:
        if Path(dirname).exists():
            print(f"✓ {dirname}/ directory exists")
        else:
            print(f"✗ {dirname}/ directory missing")
            all_exist = False

    return all_exist


def main():
    print("=" * 60)
    print("Master Creator MVP - Setup Verification")
    print("=" * 60)
    print()

    results = []

    print("Checking Python version...")
    results.append(check_python_version())
    print()

    print("Checking required directories...")
    results.append(check_directories())
    print()

    print("Checking core dependencies...")
    packages = [
        ("anthropic", "anthropic"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("sqlalchemy", "sqlalchemy"),
        ("python-dotenv", "dotenv"),
    ]

    for package_name, import_name in packages:
        results.append(check_package(package_name, import_name))
    print()

    print("Checking optional dependencies...")
    optional_packages = [
        ("psycopg2-binary", "psycopg2"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
    ]

    for package_name, import_name in optional_packages:
        check_package(package_name, import_name)
    print()

    print("Checking configuration...")
    results.append(check_env_file())
    print()

    print("=" * 60)
    if all(results):
        print("✓ All checks passed! Ready to start server.")
        print()
        print("Run: start_server.bat")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        print()
        print("To fix:")
        print("  1. Run: setup_windows.bat")
        print("  2. Edit .env and add your API key")
        print("  3. Run this script again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
