# Storybook Assistant Plugin - Development Guidelines

## Version Management

**⚠️ CRITICAL: Always bump version before pushing to GitHub**

Before committing and pushing any changes to GitHub:

1. **Update version in `.claude-plugin/plugin.json`**
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - MAJOR: Breaking changes
   - MINOR: New features (backwards compatible)
   - PATCH: Bug fixes

2. **Update version badge in `README.md`**
   - Change badge from `version-X.Y.Z` to new version

3. **Document changes**
   - Add entry to CHANGELOG.md (if exists)
   - Update SOTA_IMPLEMENTATION_COMPLETE.md if adding features

4. **Verify all files are consistent**
   - plugin.json version
   - README.md badge
   - marketplace.json (if version mentioned)

**Example workflow:**
```bash
# 1. Bump version in plugin.json (e.g., 2.0.0 → 2.1.0)
# 2. Update README badge
# 3. Commit and push
git add .
git commit -m "Bump version to 2.1.0: Added XYZ feature"
git push
```

## Plugin Development Guidelines

### Adding New Skills

1. Create skill directory: `skills/skill-name/`
2. Add `SKILL.md` with third-person description and trigger phrases
3. Add supporting files: `scripts/`, `examples/`, `references/`, `templates/`
4. Update `plugin.json` skills array
5. Test skill loading and triggering

### Adding New Commands

1. Create command file: `commands/command-name.md`
2. Add frontmatter with `description`, `allowed-tools`, `argument-hint`
3. Write instructions FOR Claude (not TO user)
4. Update `plugin.json` commands array
5. Test command execution

### Adding New Agents

1. Create agent file: `agents/agent-name.md`
2. Add frontmatter: `description`, `whenToUse`, `color`, `model`, `tools`
3. Write comprehensive system prompt
4. Update `plugin.json` agents array
5. Test agent triggering with example scenarios

### Code Quality Standards

- **Python scripts**: Use type hints, docstrings, proper error handling
- **TypeScript templates**: Use strict typing, React best practices
- **WCAG compliance**: All generated components must be accessible
- **Security**: No hardcoded credentials, use environment variables
- **Portability**: Always use `${CLAUDE_PLUGIN_ROOT}` in paths

### Testing Checklist

Before pushing:
- [ ] Version bumped in plugin.json
- [ ] README.md version badge updated
- [ ] No Python cache files (`__pycache__/`)
- [ ] No sensitive data in code
- [ ] All new skills/commands/agents added to plugin.json
- [ ] Tested locally with `claude --plugin-dir .`
- [ ] All files use proper naming conventions (kebab-case)

## Maintenance Notes

### Current Version: 2.0.0

**Features:**
- 14 skills (7 original + 7 SOTA 2026)
- 2 autonomous agents
- 8 user commands
- Vision AI design-to-code
- Natural language component generation
- AI-powered accessibility remediation
- React Server Components (React 19, Next.js 15)
- Dark mode generation
- Performance analysis
- CI/CD pipeline generation

### Dependencies

**Required:**
- Node.js ≥ 20.0.0
- npm ≥ 10.0.0

**Optional:**
- OPENROUTER_API_KEY (for visual design features)
- ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN (for AI features)

### Support & Documentation

- **Repository**: https://github.com/flight505/storybook-assistant-plugin
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: See README.md and SOTA_IMPLEMENTATION_COMPLETE.md
