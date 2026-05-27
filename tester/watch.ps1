<#
  Bi Vương — Theo dõi GitHub Releases, TỰ ĐỘNG cài APK mỗi khi có build mới vào điện thoại.
  Dùng:  powershell -ExecutionPolicy Bypass -File tester\watch.ps1
  Ctrl+C để dừng.
#>
param(
  [string]$Repo = "snape1987/app1",
  [int]$IntervalSec = 60
)
$ErrorActionPreference = "Continue"
$last = ""
Write-Host "Theo doi $Repo moi $IntervalSec giay. Ctrl+C de dung."
while ($true) {
  try {
    $tag = (gh release view --repo $Repo --json tagName --jq ".tagName" 2>$null)
  } catch {
    $tag = ""
  }
  if ($tag -and $tag -ne $last) {
    if ($last -ne "") {
      Write-Host ("Build moi: " + $tag + " -> dang cai...")
      & (Join-Path $PSScriptRoot "install_latest.ps1") -Repo $Repo
    } else {
      Write-Host ("Ban hien tai: " + $tag + " (cho build ke tiep)")
    }
    $last = $tag
  }
  Start-Sleep -Seconds $IntervalSec
}
