# Sobe a API MindTrack na porta 3000 (Windows).
# Python 3.11 ou 3.12 (o 3.14 nao instala pydantic deste projeto).

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Find-PythonLauncher {
    $saidas = & py -0p 2>$null
    if (-not $saidas) { return $null }

    foreach ($linha in $saidas) {
        if ($linha -match '3\.(11|12)\s+\*\s+(.+\.exe)') {
            return @{ Args = @('-3.' + $Matches[1]); Exe = $Matches[2].Trim() }
        }
        if ($linha -match '3\.(11|12)\s+(.+\.exe)') {
            return @{ Args = @('-3.' + $Matches[1]); Exe = $Matches[2].Trim() }
        }
    }
    return $null
}

$launcher = Find-PythonLauncher

if (-not $launcher) {
    Write-Host ""
    Write-Host "Python 3.11 ou 3.12 nao encontrado." -ForegroundColor Red
    Write-Host "Sua maquina so tem Python 3.14, que nao funciona com este backend." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Instale Python 3.12 (marque 'Add to PATH'):" -ForegroundColor Cyan
    Write-Host "  winget install Python.Python.3.12 --accept-package-agreements" -ForegroundColor White
    Write-Host "  https://www.python.org/downloads/release/python-3120/" -ForegroundColor White
    Write-Host ""
    Write-Host "Depois feche e abra o PowerShell e rode de novo:" -ForegroundColor Cyan
    Write-Host "  .\start-api.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "Usando Python: $($launcher.Exe)" -ForegroundColor Gray

if (-not (Test-Path .venv\Scripts\python.exe)) {
    Write-Host "Criando ambiente virtual (.venv) ..."
    if ($launcher.Args) {
        & py @($launcher.Args) -m venv .venv
    } else {
        & $launcher.Exe -m venv .venv
    }
}

$py = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$pip = Join-Path $PSScriptRoot ".venv\Scripts\pip.exe"

Write-Host "Instalando dependencias (pode demorar na primeira vez) ..."
& $pip install -r requirements.txt

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}

Write-Host ""
Write-Host "API: http://127.0.0.1:3000" -ForegroundColor Green
Write-Host "Docs: http://127.0.0.1:3000/docs" -ForegroundColor Green
Write-Host "Pressione Ctrl+C para parar." -ForegroundColor Gray
Write-Host ""

& (Join-Path $PSScriptRoot ".venv\Scripts\uvicorn.exe") src.main:app --reload --host 0.0.0.0 --port 3000
