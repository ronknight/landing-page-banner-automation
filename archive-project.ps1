# PowerShell script to archive project with timestamped folder
# Usage: .\archive-project.ps1
# Output: Creates timestamped folder in archive/ with complete project snapshot

# Get current directory
$ProjectPath = Get-Location
$ArchivePath = Join-Path $ProjectPath "archive"

# Generate timestamp in format YYYY-MM-DD_HHmmss
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$ArchiveFolder = Join-Path $ArchivePath $Timestamp

# Create archive directory if it doesn't exist
if (-not (Test-Path $ArchivePath)) {
    New-Item -ItemType Directory -Path $ArchivePath -Force | Out-Null
    Write-Host "Created archive directory: $ArchivePath"
}

# Check if timestamped archive already exists
if (Test-Path $ArchiveFolder) {
    Write-Host "Archive directory already exists: $ArchiveFolder"
    exit 1
}

# Create timestamped archive directory
New-Item -ItemType Directory -Path $ArchiveFolder -Force | Out-Null
Write-Host "Created archive directory: $ArchiveFolder"

# Define exclude patterns
$ExcludePatterns = @(".git", "archive", ".venv", "__pycache__", ".pyc", ".DS_Store", "node_modules", "target", "build", "dist", ".vscode", ".cursor", ".windsurf", ".cline", ".agent", ".agents")

# Get all items in project root
$items = Get-ChildItem -Force

$totalItems = 0
foreach ($item in $items) {
    $itemName = $item.Name
    
    # Check if item should be excluded
    $shouldExclude = $false
    foreach ($pattern in $ExcludePatterns) {
        if ($itemName -eq $pattern) {
            $shouldExclude = $true
            break
        }
    }
    
    if ($shouldExclude) {
        continue
    }
    
    # Copy item to archive folder
    $destination = Join-Path $ArchiveFolder $itemName
    if ($item.PSIsContainer) {
        Copy-Item -Path $item.FullName -Destination $destination -Recurse -Force
    } else {
        Copy-Item -Path $item.FullName -Destination $destination -Force
    }
    $totalItems++
}

Write-Host "Archive created successfully at: $ArchiveFolder"
Write-Host "$totalItems items archived"
