@echo off
REM setup.bat - Interactive setup for adding a new provider key

echo ====================================
echo  free-ai-router - Setup Wizard
echo ====================================
echo.
echo Select a provider to configure:
echo.
echo   1. GitHub Models   (https://github.com/settings/personal-access-tokens)
echo   2. Google Gemini   (https://aistudio.google.com/apikey)
echo   3. Groq            (https://console.groq.com/keys)
echo   4. OpenRouter      (https://openrouter.ai/keys)
echo   0. Cancel
echo.

set /p choice="Choice [0-4]: "

if "%choice%"=="0" exit /b 0
if "%choice%"=="1" goto github
if "%choice%"=="2" goto gemini
if "%choice%"=="3" goto groq
if "%choice%"=="4" goto openrouter
echo Invalid choice.
pause
exit /b 1

:github
set /p key="Enter GitHub token (github_pat_...): "
if "%key%"=="" goto github_empty
> "github_models.key.txt" echo %key%
echo Saved to github_models.key.txt
echo Run: python smart_router.py --status to verify
pause
exit /b 0

:gemini
set /p key="Enter Gemini API key (AIzaSy...): "
if "%key%"=="" goto empty
> "gemini.key.txt" echo %key%
echo Saved to gemini.key.txt
pause
exit /b 0

:groq
set /p key="Enter Groq API key (gsk_...): "
if "%key%"=="" goto empty
> "groq.key.txt" echo %key%
echo Saved to groq.key.txt
pause
exit /b 0

:openrouter
set /p key="Enter OpenRouter API key (sk-or-...): "
if "%key%"=="" goto empty
> "openrouter.key.txt" echo %key%
echo Saved to openrouter.key.txt
pause
exit /b 0

:github_empty
:empty
echo No key provided, cancelled.
pause
exit /b 1
