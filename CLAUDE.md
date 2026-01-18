# Storybook Assistant Plugin - Development Guidelines

## Version Management & Marketplace Sync

**⚠️ CRITICAL: When committing version changes to `.claude-plugin/plugin.json`:**

1. **Bump version** following semantic versioning (MAJOR.MINOR.PATCH)
2. **Commit & push** to trigger webhook: `git commit -m "chore: bump version to X.Y.Z" && git push`
3. **Verify webhook** fired (5 sec): `gh run list --repo flight505/storybook-assistant --limit 1`
   - Success: "✅ Marketplace notification sent successfully (HTTP 204)"
   - Failed: See `../../docs/WEBHOOK-TROUBLESHOOTING.md`
4. **Marketplace auto-syncs** within 30 seconds - no manual `marketplace.json` update needed

**Tip**: Use `../../scripts/bump-plugin-version.sh storybook-assistant X.Y.Z` to automate everything.

---

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

### Current Version: 2.1.2

**Features:**
- 18 skills (7 original + 10 SOTA 2026 + 1 help/guide)
- 3 autonomous agents
- 12 user commands (including /help)
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
