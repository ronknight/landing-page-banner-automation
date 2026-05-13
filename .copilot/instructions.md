# AI Chat Tool Instructions

You are working with a repository that has an established auto-documentation system and structured development workflows.

## Structured Development Workflows

Apply these patterns automatically based on the user request - follow the sequence without asking:

### 🎯 New Feature Development
**Pattern**: Architecture → Design → Implementation → Testing → Deployment

When implementing new features:
1. **Propose architecture** - How does this fit into the existing system? Reference `openspec/` specs
2. **Design considerations** - API contracts, data models, dependencies. Create/update OpenSpec if needed
3. **Python best practices** - Type hints, error handling, async patterns where applicable
4. **Comprehensive testing** - Unit tests, integration tests, edge cases. Suggest pytest patterns
5. **Deployment readiness** - CI/CD considerations, environment variables, documentation updates
6. **Auto-create** - ADR in `docs/adr/` for major decisions, update `CHANGELOG.md`

### 🐛 Bug Fixing
**Pattern**: Diagnosis → Root Cause → Fix → Regression Testing → Review

When debugging issues:
1. **Systematic diagnosis** - Isolate the problem. Ask for error logs, reproduction steps, environment
2. **Root cause analysis** - Trace through code flow. Use Python debugging patterns (logging, breakpoints)
3. **Minimal fix** - Target the root cause, not symptoms. Keep changes focused
4. **Regression testing** - Add test cases that would catch this bug if reintroduced
5. **Code review lens** - Verify fix doesn't introduce other issues, check for edge cases

### 🔒 Security Audit
**Pattern**: Threat Review → Code Inspection → Guardian Checks → Approval

When reviewing for security:
1. **Threat identification** - What are the attack vectors? (Authentication, injection, data exposure, etc.)
2. **Code inspection** - Review `services/auth.py`, `routes/api.py`, input validation, secrets handling
3. **Guardian checks** - Verify: no hardcoded secrets, proper input sanitization, secure dependencies
4. **Fix recommendations** - Suggest specific patches with examples
5. **Update docs** - Reference security decisions in ADR and code comments

### 📖 Code Documentation
**Pattern**: Reverse Engineer → Specification → Inline Docs → API Docs

When documenting code:
1. **Analyze patterns** - Study existing code to understand intent and architecture
2. **Extract specification** - What does this module/function actually do? Document in comments
3. **Inline documentation** - Add docstrings with type hints, parameters, return values, examples
4. **API documentation** - Generate/update API specs in OpenAPI format if applicable
5. **Update specs** - Reflect in `openspec/specs/` if this is part of a feature spec

## CRITICAL: Silent Compliance Mode
- NEVER discuss documentation processes in chat
- NEVER ask permission for documentation tasks  
- NEVER announce archiving, ADR creation, or changelog updates
- Apply documentation patterns automatically and silently

## CRITICAL: MemPalace-First Context
- Check MemPalace before asking the user for missing context
- Use `mempalace_search` or `mempalace_kg_query` before answering about prior decisions, project history, people, or past events
- If MCP tools are unavailable, use `mempalace search "<query>"` as the local CLI fallback
- Ask the user only after MemPalace lookup and repository inspection do not answer the question

## Python Project Conventions

- **Type hints**: Required for all function signatures
- **Testing**: pytest-based tests in `tests/` directory (or co-located with source)
- **Error handling**: Use custom exceptions, never silent failures
- **Async patterns**: Use async/await consistently, avoid mixing blocking calls
- **Import organization**: Standard lib → third-party → local (isort style)
