#!/bin/bash

# Fennec Framework - PyPI Publishing Script
# This script automates the process of publishing to PyPI

set -e  # Exit on error

echo "🦊 Fennec Framework - PyPI Publishing Script"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if required tools are installed
echo "Checking required tools..."
command -v python3 >/dev/null 2>&1 || { print_error "Python 3 is required but not installed."; exit 1; }
command -v pip >/dev/null 2>&1 || { print_error "pip is required but not installed."; exit 1; }

print_success "All required tools are installed"
echo ""

# Install/upgrade build tools
echo "Installing/upgrading build tools..."
pip install --upgrade pip setuptools wheel twine build
print_success "Build tools updated"
echo ""

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info fennec_framework.egg-info
print_success "Previous builds cleaned"
echo ""

# Run tests (if test file exists)
if [ -f "test_framework.py" ]; then
    echo "Running tests..."
    python test_framework.py || { print_error "Tests failed!"; exit 1; }
    print_success "All tests passed"
    echo ""
fi

# Build the package
echo "Building package..."
python -m build
print_success "Package built successfully"
echo ""

# List built files
echo "Built files:"
ls -lh dist/
echo ""

# Ask which repository to upload to
echo "Where do you want to publish?"
echo "1) TestPyPI (recommended for testing)"
echo "2) PyPI (production)"
echo "3) Both (TestPyPI first, then PyPI)"
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo ""
        echo "Uploading to TestPyPI..."
        python -m twine upload --repository testpypi dist/*
        print_success "Uploaded to TestPyPI"
        echo ""
        print_warning "Test installation with:"
        echo "pip install --index-url https://test.pypi.org/simple/ --no-deps fennec-framework"
        ;;
    2)
        echo ""
        read -p "Are you sure you want to publish to PyPI? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo "Uploading to PyPI..."
            python -m twine upload dist/*
            print_success "Uploaded to PyPI"
            echo ""
            print_success "Package published successfully!"
            echo "View at: https://pypi.org/project/fennec-framework/"
            echo ""
            print_warning "Install with:"
            echo "pip install fennec-framework"
        else
            print_warning "Publication cancelled"
        fi
        ;;
    3)
        echo ""
        echo "Uploading to TestPyPI first..."
        python -m twine upload --repository testpypi dist/*
        print_success "Uploaded to TestPyPI"
        echo ""
        print_warning "Please test the package from TestPyPI:"
        echo "pip install --index-url https://test.pypi.org/simple/ --no-deps fennec-framework"
        echo ""
        read -p "Press Enter after testing to continue to PyPI, or Ctrl+C to cancel..."
        echo ""
        echo "Uploading to PyPI..."
        python -m twine upload dist/*
        print_success "Uploaded to PyPI"
        echo ""
        print_success "Package published successfully!"
        echo "View at: https://pypi.org/project/fennec-framework/"
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=============================================="
print_success "Publishing complete! 🎉"
echo "Built with ❤️ in Tunisia 🇹🇳"
echo "=============================================="
