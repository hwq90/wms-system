@echo off
echo Verifying Python installation...
echo.

echo 1. Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found
    echo Please restart command prompt after installation
    goto :end
)
echo OK: Python is installed

echo.
echo 2. Checking pip...
python -m pip --version
if %errorlevel% neq 0 (
    echo WARNING: pip not working
    echo Try: python -m ensurepip --upgrade
    goto :end
)
echo OK: pip is working

echo.
echo 3. Ready to install dependencies...
echo Run: python -m pip install Pillow numpy

:end
echo.
echo Press any key to continue...
pause >nul