# Application Archiving Guide

## Purpose

This project uses timestamped directory snapshots for local version control and safe rollback capability. Before making significant changes to the codebase, create an archive to preserve the application state at that point in time.

## Archive Location

All project archives are stored in the `archive/` directory at the project root:
```
archive/
├── 2026-04-07_143022/     # Example: April 7, 2026 at 14:30:22 UTC
├── 2026-04-08_091545/     # Later archive  
└── 2026-04-10_162130/     # Another snapshot
```

**Archive Naming Convention**: `YYYY-MM-DD_HHmmss`
- `YYYY-MM-DD`: ISO date (e.g., 2026-04-07)
- `HHmmss`: Hour, minute, second in UTC (e.g., 143022 = 14:30:22)
- Example full path: `archive/2026-04-07_143022/`

## Creating an Archive

### Method 1: Automated Shell Script (Recommended)

The `archive-project.sh` script automates the archiving process:

```bash
./archive-project.sh
```

**What the script does**:
1. Creates a timestamped subfolder in `archive/` directory
2. Recursively copies all project files to the archive
3. Excludes: `.git/`, `.venv/`, `__pycache__/`, `*.pyc`, `.DS_Store`, `node_modules/`, `target/`, `build/`, `dist/`
4. Displays completion message with archive path

**Example output**:
```
Archive created successfully at: archive/2026-04-07_143022/
45 items archived
```

### Restoration

**Full Project Restoration**:
```powershell
# Copy entire archived project back to working directory
Copy-Item -Path "archive\2026-04-07_143022\*" -Destination "." -Recurse -Force
```

**Selective File Restoration**:
```powershell  
# Restore specific files
Copy-Item -Path "archive\2026-04-07_143022\src\critical-file.py" -Destination "src\critical-file.py"
```

## When to Archive

- Before major refactoring or architectural changes
- Before upgrading dependencies or frameworks
- Before experimental feature development
- Before production deployments
- AI tools automatically suggest archiving for significant changes

## Cleanup Strategy

Archives can accumulate over time. Consider:
- Keep last 10 archives for quick rollback  
- Archive older snapshots to external backup if needed
- Monitor disk space usage in `archive/` directory
- The `archive/` directory is automatically added to `.gitignore` to prevent repo bloat
- Archives remain local for fast rollback while keeping remote repository clean

## Bloat Management

**Repository Size**: Archives are excluded from git commits via `.gitignore`
**Local Storage**: Each archive = full project copy (~5-50MB depending on project size)  
**Cleanup Commands**:
```powershell
# Keep only last 5 archives
Get-ChildItem archive\ | Sort-Object CreationTime | Select-Object -SkipLast 5 | Remove-Item -Recurse

# Remove archives older than 30 days  
Get-ChildItem archive\ | Where-Object CreationTime -lt (Get-Date).AddDays(-30) | Remove-Item -Recurse
```