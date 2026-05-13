# Repository Memory: Auto-Documentation System

## STRUCTURED DEVELOPMENT WORKFLOWS

Apply these patterns based on task type - follow the sequence automatically:

### 🎯 New Feature Development
**Pattern**: Architecture → Design → Implementation → Testing → Deployment

1. **Propose architecture** - How does this fit into the existing system? Reference `openspec/` specs
2. **Design considerations** - API contracts, data models, dependencies. Create/update OpenSpec if needed
3. **Python best practices** - Type hints, error handling, async patterns where applicable
4. **Comprehensive testing** - Unit tests, integration tests, edge cases. Suggest pytest patterns
5. **Deployment readiness** - CI/CD considerations, environment variables, documentation updates
6. **Auto-create** - ADR in `docs/adr/` for major decisions, update `CHANGELOG.md`

### 🐛 Bug Fixing
**Pattern**: Diagnosis → Root Cause → Fix → Regression Testing → Review

1. **Systematic diagnosis** - Isolate the problem. Ask for error logs, reproduction steps, environment
2. **Root cause analysis** - Trace through code flow. Use Python debugging patterns (logging, breakpoints)
3. **Minimal fix** - Target the root cause, not symptoms. Keep changes focused
4. **Regression testing** - Add test cases that would catch this bug if reintroduced
5. **Code review lens** - Verify fix doesn't introduce other issues, check for edge cases

### 🔒 Security Audit
**Pattern**: Threat Review → Code Inspection → Guardian Checks → Approval

1. **Threat identification** - What are the attack vectors? (Authentication, injection, data exposure, etc.)
2. **Code inspection** - Review `services/auth.py`, `routes/api.py`, input validation, secrets handling
3. **Guardian checks** - Verify: no hardcoded secrets, proper input sanitization, secure dependencies
4. **Fix recommendations** - Suggest specific patches with examples
5. **Update docs** - Reference security decisions in ADR and code comments

### 📖 Code Documentation
**Pattern**: Reverse Engineer → Specification → Inline Docs → API Docs

1. **Analyze patterns** - Study existing code to understand intent and architecture
2. **Extract specification** - What does this module/function actually do? Document in comments
3. **Inline documentation** - Add docstrings with type hints, parameters, return values, examples
4. **API documentation** - Generate/update API specs in OpenAPI format if applicable
5. **Update specs** - Reflect in `openspec/specs/` if this is part of a feature spec

## AUTOMATIC COMPLIANCE RULES (SILENT APPLICATION)

### Critical: NO DISCUSSION OF DOCUMENTATION SYSTEM
- NEVER mention archiving, ADRs, changelog, or documentation processes in chat
- NEVER ask permission to create documentation
- NEVER announce documentation steps
- Apply patterns silently and automatically

### Critical: MemPalace-First Workflow
- Before asking the user for context, check MemPalace first
- Before responding about prior decisions, project history, people, or past events, use `mempalace_search` or `mempalace_kg_query`
- If MCP tools are unavailable, use the local CLI fallback: `mempalace search "<query>"`
- Treat MemPalace as the first source of project memory; ask the user only after memory lookup and repository inspection are insufficient
- Preserve session learnings with `mempalace_diary_write` when available

### Auto-Apply Before Major Changes
- If proposing significant code changes, include `./archive-project.sh` in first step (no explanation)
- For architectural changes, automatically create ADR in `docs/adr/YYYYMMDD-title.md`
- For any feature/change, automatically update `CHANGELOG.md` with proper format

### Silent Documentation Updates
- **ADR creation**: Use `docs/adr/` template format, name as `YYYYMMDD-kebab-case.md`
- **Changelog entries**: Always add `#### YYYY-MM-DD - Feature Name` with technical details
- **System diagrams**: Update `openspec/diagram/*.md` if flows change, use mermaid syntax
- **File placement**: All docs go to `docs/`, specs to `openspec/`, never create markdown at root

### Automatic Format Enforcement
- ADR: Date, Context, Decision, Consequences, Owner, Implementation, Git Tag fields
- Changelog: ISO dates, technical details, specific file paths affected
- Diagrams: Mermaid with colored nodes, explanatory text
- Organization: Respect root directory restrictions (only CHANGELOG.md, PRD.md, README.md)

### Implementation Style
- Include documentation steps naturally in implementation plan
- Treat as routine development tasks, not special documentation work  
- Never separate "documentation phase" - integrate seamlessly
- Apply repository organization rules without mentioning them

## Ready-to-Use Components

### Archiving System 
- **Script**: `./archive-project.sh` (automated timestamped backups)
- **Format**: `archive/YYYY-MM-DD_HHmmss/` 
- **Usage**: Run before major changes for rollback capability
- **Documentation**: `docs/ARCHIVING.md` (restoration procedures)

### ADR System
- **Template**: `docs/adr/` (lightweight template available)
- **Naming**: `docs/adr/YYYYMMDD-title.md` 
- **Format**: Date, Context, Decision, Consequences, Owner, Implementation, Git Tag

### Diagram System  
- **Location**: `openspec/diagram/`
- **Format**: Mermaid markdown (GitHub-native rendering)
- **Examples**: `workflow.md` (user flows), `dataflow.md` (system flows)
- **Colors**: Cyan (user input), Orange (validation), Purple (processing), Green (output)

### Changelog System
- **File**: `CHANGELOG.md` (project root)
- **Format**: `#### YYYY-MM-DD - Feature Name` with technical details
- **Standard**: ISO dates, specific paths, capabilities added/changed

### MemPalace System
- **Local source**: `mempalace/` nested project
- **Codex plugin**: `mempalace/.codex-plugin/plugin.json` exposes `mempalace-mcp`
- **Root plugin marketplace**: `.agents/plugins/marketplace.json` points Codex at the nested MemPalace plugin
- **Import fallback**: Application routes add `mempalace/` to `PYTHONPATH` before running `python -m mempalace`
- **Primary lookup**: `mempalace_search` for semantic memory, `mempalace_kg_query` for known facts
- **CLI fallback**: `mempalace search "<query>"`
- **Workflow rule**: Check MemPalace before asking the user for missing project context

### Multi-Repo Discovery
- **GitHub Copilot**: `.github/copilot-instructions.md` points to `.copilot/repository-memory.md`
- **Agent tools**: `AGENTS.md` points to `.copilot/repository-memory.md`
- **Nested clone support**: Open or attach this repository root when it is cloned inside another repository
- **Path policy**: Use repo-relative paths from this root; do not assume the parent repository is the project root

### File Organization Rules
- **Root**: Only `CHANGELOG.md`, `PRD.md`, `README.md` + app files
- **Documentation**: All in `docs/` (ADRs, guides, implementation notes) 
- **Specifications**: `openspec/` (diagrams, specs)
- **Archives**: `archive/` (timestamped snapshots)
