# setup_windows.ps1 — prepares a Windows PC or an InterServer Windows VPS for the Creative Strategy OS.
#
#   powershell -ExecutionPolicy Bypass -File setup_windows.ps1 -Check     only says what is there and what is missing
#   powershell -ExecutionPolicy Bypass -File setup_windows.ps1            installs what is missing, then checks again
#
# Installs (only when missing): Python 3.11, Google Chrome, LibreOffice when Word is absent (the PDFs), the Python
# packages of requirements.txt (ffmpeg comes with imageio-ffmpeg). Never touches existing data. Official sources only:
# python.org, dl.google.com, and winget when Windows has it. The Claude app is installed by hand (claude.ai/download).
param([switch]$Check)
$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$req = Join-Path (Split-Path -Parent (Split-Path -Parent $here)) "requirements.txt"
$tmp = Join-Path $env:TEMP "cs-setup"
New-Item -ItemType Directory -Force $tmp | Out-Null

function Say($ok, $what, $fix) {
    if ($ok) { Write-Host "  [ok]   $what" -ForegroundColor Green }
    else { Write-Host "  [--]   $what" -ForegroundColor Yellow; if ($fix) { Write-Host "         -> $fix" } }
}

function Find-Python {
    foreach ($c in @("py -3.11", "python")) {
        try {
            $v = & cmd /c "$c --version 2>&1"
            if ($v -match "Python 3\.(\d+)") { if ([int]$Matches[1] -ge 11) { return $c } }
        } catch {}
    }
    return $null
}

function Has-Word { return (Test-Path "$env:ProgramFiles\Microsoft Office\root\Office16\WINWORD.EXE") -or (Test-Path "${env:ProgramFiles(x86)}\Microsoft Office\root\Office16\WINWORD.EXE") }
function Has-Office { return (Has-Word) -or (Test-Path "$env:ProgramFiles\LibreOffice\program\soffice.exe") }
function Has-Chrome { return (Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -or (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe") }
function Has-Winget { return [bool](Get-Command winget -ErrorAction SilentlyContinue) }

function Report {
    Write-Host ""
    Write-Host "Ce que cet ordinateur a :"
    $py = Find-Python
    Say ($py -ne $null) "Python 3.11 ou plus récent" "python.org/downloads (cocher « Add python.exe to PATH »)"
    if ($py) {
        $missing = & cmd /c "$py -c ""import importlib.util as u;print(' '.join(m for m in ['yaml','docx','pymupdf','PIL','av','openpyxl','faster_whisper','yt_dlp','imageio_ffmpeg','google.genai'] if not u.find_spec(m)))"" 2>&1"
        Say ([string]::IsNullOrWhiteSpace($missing)) "Paquets Python de la suite" "manquants : $missing"
    }
    Say (Has-Chrome) "Google Chrome (recherches, Claude in Chrome)" "google.com/chrome"
    Write-Host "  [??]   Claude in Chrome (l'extension) : à vérifier à la main" -ForegroundColor Cyan
    Write-Host "         -> claude.ai/chrome, « Ajouter à Chrome », connecte-toi avec ton compte Claude, puis connecte ce Chrome à Facebook, Instagram et TikTok"
    $gk = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User")
    Say (-not [string]::IsNullOrWhiteSpace($gk)) "Clé Gemini gratuite (facultative : toutes les références analysées)" "aistudio.google.com/apikey, puis : setx GEMINI_API_KEY ""<ta clé>"""
    Say (Has-Office) "Word ou LibreOffice (les PDF)" "libreoffice.org (gratuit) si Word n'est pas installé"
    $skills = Join-Path $env:USERPROFILE ".claude\skills\creative-strategist\VERSION"
    Say (Test-Path $skills) "Les skills de la suite" "suite.py install <zip> (voir le guide d'installation)"
    if (Test-Path $skills) { Write-Host ("         version " + (Get-Content $skills -First 1)) }
    $ram = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 1)
    Say ($ram -ge 7) "Mémoire : $ram Go" "8 Go conseillés pour Whisper (4 slices chez InterServer)"
    $free = [math]::Round((Get-PSDrive C).Free / 1GB, 1)
    Say ($free -ge 10) "Espace libre sur C: : $free Go" "10 Go au moins (vidéos de référence, modèle Whisper)"
    Write-Host ""
}

if ($Check) { Report; exit 0 }

Write-Host "Installation de ce qui manque…"
if (-not (Find-Python)) {
    if (Has-Winget) { winget install -e --id Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements }
    else {
        $f = Join-Path $tmp "python-3.11.9-amd64.exe"
        Invoke-WebRequest "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $f
        Start-Process $f -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_launcher=1" -Wait
    }
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}
if (-not (Has-Chrome)) {
    if (Has-Winget) { winget install -e --id Google.Chrome --silent --accept-package-agreements --accept-source-agreements }
    else {
        $f = Join-Path $tmp "chrome.msi"
        Invoke-WebRequest "https://dl.google.com/chrome/install/googlechromestandaloneenterprise64.msi" -OutFile $f
        Start-Process msiexec.exe -ArgumentList "/i `"$f`" /qn" -Wait
    }
}
if (-not (Has-Office)) {
    if (Has-Winget) { winget install -e --id TheDocumentFoundation.LibreOffice --silent --accept-package-agreements --accept-source-agreements }
    else { Write-Host "  LibreOffice : télécharge-le sur libreoffice.org (les PDF des livrables) ; sans lui, seulement les .docx." }
}
$py = Find-Python
if ($py -and (Test-Path $req)) {
    & cmd /c "$py -m pip install --upgrade pip"
    & cmd /c "$py -m pip install -r ""$req"""
} elseif (-not $py) {
    Write-Host "  Python n'est pas encore visible : ferme cette fenêtre, ouvre-en une nouvelle et relance ce script."
}
Report
Write-Host "Ensuite : installe l'app Claude (claude.ai/download), connecte-toi, puis dans un dossier produit :"
Write-Host "  python `"$env:USERPROFILE\.claude\skills\creative-strategist\scripts\ws.py`" doctor <dossier>"
