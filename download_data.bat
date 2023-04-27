@echo off
setlocal

set "url=%~1"
if not defined url set "url=https://github.com/edgarGracia/models/releases/download/v0.2.1/data.zip"

echo Downloading %url%
powershell -Command "(New-Object System.Net.WebClient).DownloadFile('%url%', 'data.zip')" || exit /b 1

echo Extracting data
powershell -c "Expand-Archive -LiteralPath 'data.zip' -DestinationPath '.' -Force" || exit /b 1

del data.zip

echo Done