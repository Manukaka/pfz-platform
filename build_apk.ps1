# DaryaSagar APK Builder
# Run as Administrator in PowerShell: .\build_apk.ps1
# Installs Android command-line tools (~200MB) then builds debug APK

param(
    [string]$AndroidSdkRoot = "C:\Android",
    [string]$MapboxToken = "YOUR_MAPBOX_TOKEN_HERE"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step { param($msg) Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "    OK: $msg" -ForegroundColor Green }
function Write-Fail { param($msg) Write-Host "    FAIL: $msg" -ForegroundColor Red; exit 1 }

Write-Host @"

  ____                        ____
 |  _ \  __ _ _ __ _   _  __|  _ \ __ _  __ _  __ _ _ __
 | | | |/ _' | '__| | | |/ _'  _ \/ _' |/ _' |/ _' | '__|
 | |_| | (_| | |  | |_| | (_| |_) | (_| | (_| | (_| | |
 |____/ \__,_|_|   \__, |\__,_____/ \__,_|\__, |\__,_|_|
                    |___/                   |___/
  APK Builder v1.0 — DaryaSagar

"@ -ForegroundColor Yellow

# ── Step 1: Java ────────────────────────────────────────────────────────────
Write-Step "Checking Java..."

$javaOk = $false
try {
    $jv = & java -version 2>&1
    if ($jv -match "version") { $javaOk = $true; Write-OK "Java found" }
} catch {}

if (-not $javaOk) {
    Write-Step "Installing Java 17 (Microsoft OpenJDK) via winget..."
    try {
        winget install Microsoft.OpenJDK.17 --accept-source-agreements --accept-package-agreements --silent
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        Write-OK "Java installed"
    } catch {
        Write-Host "    winget failed. Trying manual download..." -ForegroundColor Yellow
        $jdkUrl = "https://aka.ms/download-jdk/microsoft-jdk-17-windows-x64.zip"
        $jdkZip = "$env:TEMP\jdk17.zip"
        $jdkDir = "C:\Java\jdk17"
        Write-Host "    Downloading JDK (~180MB)..."
        Invoke-WebRequest -Uri $jdkUrl -OutFile $jdkZip
        New-Item -ItemType Directory -Force -Path $jdkDir | Out-Null
        Expand-Archive -Path $jdkZip -DestinationPath $jdkDir -Force
        $jdkBin = (Get-ChildItem $jdkDir -Filter "bin" -Recurse | Select-Object -First 1).FullName
        [System.Environment]::SetEnvironmentVariable("JAVA_HOME", (Split-Path $jdkBin), "Machine")
        $env:JAVA_HOME = Split-Path $jdkBin
        $env:PATH = "$jdkBin;$env:PATH"
        Write-OK "JDK installed at $jdkDir"
    }
}

# ── Step 2: Android command-line tools ──────────────────────────────────────
Write-Step "Setting up Android SDK at $AndroidSdkRoot..."

$cmdlineToolsDir = "$AndroidSdkRoot\cmdline-tools\latest"

if (-not (Test-Path "$cmdlineToolsDir\bin\sdkmanager.bat")) {
    Write-Host "    Downloading Android command-line tools (~150MB)..." -ForegroundColor White
    $clZip = "$env:TEMP\cmdline-tools.zip"
    $clUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
    Invoke-WebRequest -Uri $clUrl -OutFile $clZip -UseBasicParsing
    Write-Host "    Extracting..."
    $clTemp = "$env:TEMP\cmdline-tools-extract"
    if (Test-Path $clTemp) { Remove-Item $clTemp -Recurse -Force }
    Expand-Archive -Path $clZip -DestinationPath $clTemp -Force
    New-Item -ItemType Directory -Force -Path "$AndroidSdkRoot\cmdline-tools" | Out-Null
    Move-Item "$clTemp\cmdline-tools" "$cmdlineToolsDir" -Force
    Write-OK "Command-line tools extracted"
} else {
    Write-OK "Command-line tools already present"
}

# Set environment variables for this session
$env:ANDROID_SDK_ROOT = $AndroidSdkRoot
$env:ANDROID_HOME     = $AndroidSdkRoot
$env:PATH             = "$cmdlineToolsDir\bin;$AndroidSdkRoot\platform-tools;$env:PATH"

# Persist for future sessions
[System.Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $AndroidSdkRoot, "Machine")
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME",     $AndroidSdkRoot, "Machine")

# ── Step 3: SDK packages ─────────────────────────────────────────────────────
Write-Step "Installing Android SDK packages (platform-tools + API 34 + build-tools)..."

$sdkmanager = "$cmdlineToolsDir\bin\sdkmanager.bat"

# Accept licenses without prompt
"y`ny`ny`ny`ny`ny`ny`n" | & $sdkmanager --sdk_root="$AndroidSdkRoot" --licenses 2>&1 | Out-Null
Write-OK "Licenses accepted"

& $sdkmanager --sdk_root="$AndroidSdkRoot" "platform-tools" "platforms;android-34" "build-tools;34.0.0"
if ($LASTEXITCODE -ne 0) { Write-Fail "sdkmanager failed" }
Write-OK "SDK packages installed"

# ── Step 4: Update local.properties ─────────────────────────────────────────
Write-Step "Updating local.properties..."

$localProps = "flutter_app\android\local.properties"
$flutterSdk = "C:\Users\manoj\.puro\envs\stable\flutter"

# Check if flutter SDK exists at expected path
if (-not (Test-Path $flutterSdk)) {
    # Try to find it
    $found = Get-ChildItem "C:\Users\manoj\.puro\envs" -Filter "flutter" -Recurse -Depth 2 -Directory -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) { $flutterSdk = $found.FullName }
}

@"
flutter.sdk=$($flutterSdk.Replace('\', '\\'))
sdk.dir=$($AndroidSdkRoot.Replace('\', '\\'))
MAPBOX_ACCESS_TOKEN=$MapboxToken
"@ | Set-Content $localProps -Encoding UTF8

Write-OK "local.properties written"

# ── Step 5: Flutter pub get ──────────────────────────────────────────────────
Write-Step "Running flutter pub get..."

$flutterExe = "$flutterSdk\bin\flutter.bat"
if (-not (Test-Path $flutterExe)) {
    # Try without .bat
    $flutterExe = "$flutterSdk\bin\flutter"
}

Push-Location "flutter_app"
try {
    & $flutterExe pub get
    if ($LASTEXITCODE -ne 0) { Write-Fail "flutter pub get failed" }
    Write-OK "Dependencies resolved"

    # ── Step 6: Build debug APK ──────────────────────────────────────────────
    Write-Step "Building debug APK (this takes 3-8 minutes on first build)..."

    & $flutterExe build apk --debug `
        "--dart-define=API_BASE_URL=http://localhost:8000" `
        "--dart-define=WS_BASE_URL=ws://localhost:8000" `
        "--dart-define=SUPABASE_URL=" `
        "--dart-define=SUPABASE_ANON_KEY=" `
        "--dart-define=MAPBOX_ACCESS_TOKEN=$MapboxToken" `
        "--dart-define=SENTRY_DSN=" `
        "--dart-define=ENV=debug"

    if ($LASTEXITCODE -ne 0) { Write-Fail "flutter build apk failed" }

} finally {
    Pop-Location
}

# ── Done ─────────────────────────────────────────────────────────────────────
$apkPath = "flutter_app\build\app\outputs\flutter-apk\app-debug.apk"
$apkFull = Join-Path (Get-Location) $apkPath

if (Test-Path $apkFull) {
    $sizeMB = [math]::Round((Get-Item $apkFull).Length / 1MB, 1)
    Write-Host "`n" -NoNewline
    Write-Host "  ╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "  ║  APK READY!  ($sizeMB MB)                                  ║" -ForegroundColor Green
    Write-Host "  ║                                                          ║" -ForegroundColor Green
    Write-Host "  ║  $apkPath" -ForegroundColor Green
    Write-Host "  ║                                                          ║" -ForegroundColor Green
    Write-Host "  ║  INSTALL OPTIONS:                                        ║" -ForegroundColor Green
    Write-Host "  ║  1. USB: adb install $apkPath" -ForegroundColor Green
    Write-Host "  ║  2. Share APK to phone via WhatsApp/email and tap it     ║" -ForegroundColor Green
    Write-Host "  ║  3. Copy to phone storage, open with Files app           ║" -ForegroundColor Green
    Write-Host "  ╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green

    # Copy to desktop for easy access
    $desktop = [Environment]::GetFolderPath("Desktop")
    Copy-Item $apkFull "$desktop\DaryaSagar-debug.apk" -Force
    Write-Host "`n  ALSO COPIED TO DESKTOP: DaryaSagar-debug.apk" -ForegroundColor Yellow
    Write-Host "  (Share this file to your phone via WhatsApp/email/USB)`n" -ForegroundColor Yellow

    # Open ADB install option
    Write-Host "  To install via USB (phone must have USB debugging ON):" -ForegroundColor White
    Write-Host "  $AndroidSdkRoot\platform-tools\adb.exe install `"$apkFull`"`n" -ForegroundColor White
} else {
    Write-Fail "APK not found at expected path — check build output above"
}
