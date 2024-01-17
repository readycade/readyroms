@echo off
setlocal enabledelayedexpansion

set "extractPath=\\RECALBOX\share"
set "tempExtractPath=%~dp0Temp"
set "biosExtractPath=%APPDATA%\readycade\bios"

REM Check if a file path was passed as an argument
if "%~1"=="" (
    set /p "romFile=Drag and drop the ROM file here: "
    if "!romFile!"=="" (
        echo No file path provided. Exiting script.
        pause
        exit /b
    )
) else (
    set "romFile=%~1"
)

REM Display the dropped or input file path
echo You selected the file: !romFile!

REM Pass the selected file path to your main batch script (EZ-Roms.bat)
call EZ_Roms.bat "!romFile!"

endlocal
