# Install Git hooks for documentation compliance
# Usage: .\install-hooks.ps1

$HookSource = Join-Path (Join-Path $PSScriptRoot "hooks") "pre-commit"
$HookTarget = Join-Path (Join-Path $PSScriptRoot ".git") (Join-Path "hooks" "pre-commit")

if (-not (Test-Path $HookSource)) {
    Write-Host "Error: hooks/pre-commit not found" -ForegroundColor Red
    exit 1
}

Copy-Item -Path $HookSource -Destination $HookTarget -Force
Write-Host "Installed pre-commit hook to .git/hooks/pre-commit" -ForegroundColor Green
Write-Host ""
Write-Host "Documentation compliance will now be checked before every commit."
Write-Host "Use 'git commit --no-verify' to bypass in emergencies."
