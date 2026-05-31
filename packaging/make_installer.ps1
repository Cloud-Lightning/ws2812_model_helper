param(
    [string]$SourceExe = "$PSScriptRoot\..\dist\Ws2812ModelHelper.exe",
    [string]$OutputDir = "$PSScriptRoot\..\release",
    [string]$IsccPath = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)

$ErrorActionPreference = "Stop"

$sourceExePath = Resolve-Path -LiteralPath $SourceExe
$outputDirPath = [System.IO.Path]::GetFullPath($OutputDir)
$issPath = Join-Path $PSScriptRoot "ws2812_model_helper.iss"

if (-not (Test-Path -LiteralPath $IsccPath)) {
    $found = Get-ChildItem -Path "$env:LOCALAPPDATA\Programs", "$env:ProgramFiles", "${env:ProgramFiles(x86)}" -Recurse -Filter ISCC.exe -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $IsccPath = $found.FullName
    } else {
        throw "ISCC.exe was not found. Install Inno Setup 6 first."
    }
}

New-Item -ItemType Directory -Force -Path $outputDirPath | Out-Null
Remove-Item -LiteralPath (Join-Path $outputDirPath "Ws2812ModelHelperSetup.exe") -Force -ErrorAction SilentlyContinue

& $IsccPath `
    "/DSourceExe=$sourceExePath" `
    "/DOutputDir=$outputDirPath" `
    $issPath

$setupPath = Join-Path $outputDirPath "Ws2812ModelHelperSetup.exe"
if (-not (Test-Path -LiteralPath $setupPath)) {
    throw "Installer was not created: $setupPath"
}

Get-Item -LiteralPath $setupPath
