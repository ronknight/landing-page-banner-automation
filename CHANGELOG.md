# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### 2026-06-05 - Event Background Selection
- Added per-event `background` paths to `events.json`.
- Updated banner generation to load the selected event background from configuration with legacy `bg.png` fallback.

#### 2026-06-05 - Slot Assignment Fix
- Fixed product placement so missing or failed TIF files no longer skip the first available banner slot.

#### 2026-05-13 - Auto-Documentation System
- Added timestamped archive directory system (`archive/<YYYY-MM-DD_HHmmss>/`) for local version control snapshots
- Created `archive-project.sh` shell script for automated project archiving
- Implemented lightweight ADR (Architecture Decision Record) system in `docs/adr/`
- Added mermaid diagram support in `openspec/diagram/` for GitHub-native rendering
- Configured AI chat tools for automatic documentation compliance
- Established file organization rules: documentation in `docs/`, specifications in `openspec/`, archives in `archive/`
