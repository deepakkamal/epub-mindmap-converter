@echo off
echo 🧪 Mind Map Framework - Quick Deployment Test
echo ============================================

cd /d "%~dp0"

:: Activate conda environment
call conda activate mind_map

:: Run deployment test
python deployment_test.py

echo.
echo ✅ Test completed!
pause