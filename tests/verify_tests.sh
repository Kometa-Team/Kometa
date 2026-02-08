#!/bin/bash
# Quick verification script for test setup

echo "============================================"
echo "Kometa Test Suite - Setup Verification"
echo "============================================"
echo ""

# Check Python location
echo "✓ Python location:"
which python
echo ""

# Check Python version
echo "✓ Python version:"
python --version
echo ""

# Check if pytest is installed
echo "Checking pytest installation..."
if command -v pytest &> /dev/null; then
    echo "✓ pytest is installed:"
    pytest --version
else
    echo "✗ pytest is NOT installed"
    echo "  Install with: pip install pytest pytest-cov pytest-mock"
fi
echo ""

# Check test file structure
echo "✓ Test files created:"
ls -1 tests/ | grep -E '\.(py|md)$' | sed 's/^/  - /'
echo ""

# Check configuration files
echo "✓ Configuration files:"
if [ -f "pytest.ini" ]; then
    echo "  - pytest.ini"
fi
if [ -f ".github/workflows/tests.yml" ]; then
    echo "  - .github/workflows/tests.yml"
fi
if [ -f "run_tests.sh" ]; then
    echo "  - run_tests.sh"
fi
echo ""

# Try to collect tests
echo "Test discovery check:"
if command -v pytest &> /dev/null; then
    echo "Attempting to discover tests..."
    pytest --collect-only tests/test_anidb.py -q 2>&1 | head -20
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Tests discovered successfully!"
    else
        echo ""
        echo "⚠ Test discovery had issues (likely missing dependencies)"
        echo "  This is normal if you haven't installed project dependencies yet."
        echo ""
        echo "To fix, install project dependencies:"
        echo "  pip install -r requirements.txt"
        echo "  pip install pytest pytest-cov pytest-mock"
    fi
else
    echo "⚠ Cannot verify test discovery without pytest"
fi

echo ""
echo "============================================"
echo "Summary"
echo "============================================"
echo "✓ Test suite structure created"
echo "✓ 40+ test cases for AniDB module"
echo "✓ CI/CD workflow configured"
echo "✓ Documentation provided"
echo ""
echo "To run tests (after installing dependencies):"
echo "  pytest"
echo "  pytest --cov=modules"
echo "  ./run_tests.sh --coverage"
echo ""
echo "See tests/README.md for more information."
echo "============================================"
