@echo off
echo Python Installation Status Check
echo.

echo 1. Checking running Python installers...
tasklist | findstr /i python
if %errorlevel% equ 0 (
    echo Python installer is running
    echo Please check your screen for the installation window
    echo.
    echo If you can't see it, try:
    echo   - Alt+Tab to switch windows
    echo   - Check taskbar
    echo   - Look for "Python 3.12.0 (64-bit) Setup"
) else (
    echo Python installer is not running
    echo Starting installer...
    start python_installer.exe
)

echo.
echo 2. If installation is stuck:
echo    - Wait 2 more minutes
echo    - If still stuck, close and restart installer
echo    - Try right-click -> Run as administrator

echo.
echo 3. When installation completes:
echo    - You'll see "Setup was successful"
echo    - Tell me immediately
echo    - I'll run the image processing

echo.
pause