@echo off
echo Python Installation Assistant
echo.

echo 1. Starting Python installer...
echo    File: python_installer.exe
echo    Size: 26507904 bytes
echo.

echo 2. If you don't see the installer window:
echo    - Check taskbar (Alt+Tab)
echo    - Allow in antivirus if blocked
echo    - Try right-click and "Run as administrator"
echo.

echo 3. When installer appears:
echo    - Check "Add Python to PATH" (IMPORTANT!)
echo    - Click "Install Now"
echo    - Wait for completion
echo.

echo 4. After installation:
echo    - Come back here and tell me
echo    - I will run the image processing script
echo.

echo Press any key to try starting installer again...
pause >nul

start "" "python_installer.exe"

echo.
echo Installer started. Check for the window!
echo If still not visible, try:
echo 1. Task Manager -> check processes
echo 2. Reboot and try again
echo 3. Download fresh installer from python.org

pause