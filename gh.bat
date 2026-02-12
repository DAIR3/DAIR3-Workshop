@echo off
setlocal

rem ---- Check that a commit message was provided ----
if "%~1"=="" (
    echo Usage: gh "commit message"
    exit /b 1
)

rem ---- Stage all changes (including deletions) ----
git add -A

rem ---- Update your local branch from GitHub (replace "main" if your branch is different) ----
git pull origin main

rem ---- Only commit if there are staged changes ----
git diff --cached --quiet
if errorlevel 1 (
    rem %* expands to all arguments exactly as passed, including quotes
    git commit -m %*
)

rem ---- Push to DAIR3 organization repo ----
git push origin HEAD

rem ---- Push to biomathematicus repo ----
git push biomathematicus HEAD

endlocal