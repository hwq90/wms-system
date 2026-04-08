@echo off
echo Python Installation Check
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python from python.org
    echo Make sure to check "Add Python to PATH"
) else (
    echo OK: Python is installed
)

echo.
echo Checking pip...
python -m pip --version
if errorlevel 1 (
    echo ERROR: pip not found
    echo Try: python -m ensurepip --upgrade
) else (
    echo OK: pip is installed
)

echo.
echo Press any key to continue...
pause >nul