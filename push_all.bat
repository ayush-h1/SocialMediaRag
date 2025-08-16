@echo off
setlocal enabledelayedexpansion

REM ====== CONFIG ======
set "REPO_URL=https://github.com/ayush-h1/SocialMediaRag.git"
set "BRANCH=main"
set "COMMIT_MSG=Sync full project"
REM Set to 1 if you want to auto-enable Git LFS for large binaries
set "USE_LFS=0"
REM =====================

echo.
echo === Checking Git installation ===
where git >NUL 2>&1
if errorlevel 1 (
  echo [ERROR] Git is not installed or not on PATH. Install Git from https://git-scm.com/download/win
  exit /b 1
)

echo.
echo === Initializing git repo (if needed) ===
git rev-parse --is-inside-work-tree >NUL 2>&1
if errorlevel 1 (
  git init
)

echo.
echo === Setting default branch to %BRANCH% ===
for /f "tokens=*" %%h in ('git symbolic-ref --short HEAD 2^>NUL') do set "CUR_BRANCH=%%h"
if not defined CUR_BRANCH (
  git branch -M %BRANCH%
) else (
  if /I not "!CUR_BRANCH!"=="%BRANCH%" git branch -M %BRANCH%
)

echo.
echo === Setting remote 'origin' ===
git remote get-url origin >NUL 2>&1
if %errorlevel%==0 (
  git remote set-url origin %REPO_URL%
) else (
  git remote add origin %REPO_URL%
)

echo.
echo === Creating a sensible .gitignore (only if missing) ===
if not exist ".gitignore" (
  (
    echo # Python
    echo __pycache__/
    echo .venv/
    echo *.pyc
    echo .pytest_cache/
    echo
    echo # Node / Vite
    echo node_modules/
    echo dist/
    echo .vite/
    echo
    echo # Env / secrets
    echo .env
    echo .env.local
    echo
    echo # OS junk
    echo .DS_Store
    echo Thumbs.db
  ) > .gitignore
)

echo.
echo === Optional: Git LFS for big binaries ===
if "%USE_LFS%"=="1" (
  git lfs version >NUL 2>&1
  if errorlevel 1 (
    echo Git LFS not found. Install from https://git-lfs.com/ if you need to track large files.
  ) else (
    git lfs install
    REM Common big file patterns; adjust if needed
    git lfs track "*.pt" "*.bin" "*.onnx" "*.mp4" "*.zip" "*.tar" "*.7z"
    git add .gitattributes
  )
)

echo.
echo === Increasing push buffer (harmless) ===
git config http.postBuffer 524288000

echo.
echo === Staging all files ===
git add -A

echo.
echo === Committing ===
git commit -m "%COMMIT_MSG%"
if errorlevel 1 (
  echo (Nothing to commit or commit failed; continuing…)
)

echo.
echo === Pushing to %REPO_URL% (%BRANCH%) ===
git push -u origin %BRANCH%
if errorlevel 1 (
  echo.
  echo [ERROR] Push failed.
  echo - If you saw "file > 100 MB", use Git LFS (set USE_LFS=1 and run again).
  echo - If auth failed, run: git config --global credential.helper manager-core
  echo   then push again to sign in.
  exit /b 1
)

echo.
echo ✅ Done!
endlocal
