<#
  Bi Vương — Tải APK mới nhất từ GitHub Releases và cài vào điện thoại Android đang cắm USB.
  Yêu cầu: gh CLI (đã login), adb (Android platform-tools), điện thoại bật USB debugging.
  Dùng:  powershell -ExecutionPolicy Bypass -File tester\install_latest.ps1
#>
param(
  [string]$Repo  = "snape1987/app1",
  [string]$AppId = "com.app1.app"
)
$ErrorActionPreference = "Stop"

$tmp = Join-Path $env:TEMP "bivuong_apk"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

Write-Host "==> Tải APK mới nhất từ $Repo ..."
gh release download --repo $Repo --pattern "*.apk" --dir $tmp --clobber
$apk = Get-ChildItem $tmp -Filter *.apk | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $apk) { Write-Host "Khong tai duoc APK."; exit 1 }
Write-Host ("    APK: " + $apk.Name + " (" + [math]::Round($apk.Length / 1MB, 2) + " MB)")

Write-Host "==> Kiem tra dien thoai ..."
$devs = @()
foreach ($line in (adb devices)) {
  if ($line -match "^(\S+)\s+device$") { $devs += $Matches[1] }
}
if ($devs.Count -eq 0) {
  Write-Host "Khong thay dien thoai. Cam USB, bat USB debugging, chap nhan may tinh roi chay lai."
  exit 1
}
Write-Host ("    Thiet bi: " + ($devs -join ", "))

Write-Host "==> Cai (adb install -r) ..."
adb install -r "$($apk.FullName)"
if ($LASTEXITCODE -ne 0) { Write-Host "adb install loi."; exit 1 }

Write-Host "==> Mo app $AppId ..."
adb shell monkey -p $AppId -c android.intent.category.LAUNCHER 1 | Out-Null

Write-Host "OK - Bi Vuong da cai va mo tren dien thoai."
