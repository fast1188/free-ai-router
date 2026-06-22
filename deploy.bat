@echo off
chcp 65001 >nul
cd /d "D:\Github开源项目\free-ai-router"

echo ====================================
echo  free-ai-router - Deploy Script
echo ====================================
echo.

echo [1/5] Checking git status...
git status >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Not a git repository or git not installed
    pause
    exit /b 1
)
echo OK.
echo.

echo [2/5] Adding GitHub remote...
git remote remove github 2>nul
git remote add github https://github.com/fast1188/free-ai-router.git
echo Done.
echo.

echo [3/5] Adding Gitee remote...
git remote remove gitee 2>nul
git remote add gitee https://gitee.com/wudijia2026/free-ai-router.git
echo Done.
echo.

echo [4/5] Current remotes:
git remote -v
echo.

echo [5/5] Pushing to GitHub (will prompt for credentials)...
git push -u github main
if errorlevel 1 (
    echo.
    echo [WARNING] GitHub push failed. Reasons: repo not created, wrong PAT, or network.
    echo.
)

echo.
echo [Bonus] Pushing to Gitee...
git push -u gitee main
if errorlevel 1 (
    echo.
    echo [WARNING] Gitee push failed. Reasons: repo not created, wrong password, or network.
    echo.
)

echo.
echo ====================================
echo  Done!
echo ====================================
echo GitHub: https://github.com/fast1188/free-ai-router
echo Gitee:  https://gitee.com/wudijia2026/free-ai-router
echo ====================================
pause