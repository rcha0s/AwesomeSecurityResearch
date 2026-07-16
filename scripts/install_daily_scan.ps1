# ---------------------------------------------------------------------------
# install_daily_scan.ps1 - Register (or remove) the daily scan as a Windows
# Scheduled Task. Runs daily_scan.ps1 at a fixed local time.
#
#     powershell -ExecutionPolicy Bypass -File scripts\install_daily_scan.ps1            # install at 08:00
#     powershell -ExecutionPolicy Bypass -File scripts\install_daily_scan.ps1 -At 07:30  # custom time
#     powershell -ExecutionPolicy Bypass -File scripts\install_daily_scan.ps1 -Uninstall
# ---------------------------------------------------------------------------
param(
    [string]$At = "08:00",
    [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$taskName = "AwesomeSecurityResearch-DailyScan"
$repo = Split-Path -Parent $PSScriptRoot
$scan = Join-Path $repo "scripts\daily_scan.ps1"

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed scheduled task '$taskName'."
    return
}

if (-not (Test-Path $scan)) { throw "daily_scan.ps1 not found at $scan" }

$argStr  = '-NonInteractive -ExecutionPolicy Bypass -File "{0}"' -f $scan
$action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argStr
$trigger = New-ScheduledTaskTrigger -Daily -At $At
# Run only when a network is available; wake isn't required (skips if machine off).
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Daily AI/security research scan -> PR" -Force | Out-Null

Write-Host "Installed scheduled task '$taskName' - runs daily at $At."
Write-Host "  Run now:    Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  Inspect:    Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
Write-Host "  Logs:       scripts\logs\daily_scan_<date>.log"
Write-Host "  Remove:     powershell -File scripts\install_daily_scan.ps1 -Uninstall"
