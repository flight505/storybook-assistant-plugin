---
description: Use this skill when the user asks to "setup CI/CD", "configure GitHub Actions", "deploy Storybook", "setup Chromatic", "add visual regression to CI", "create deployment pipeline", or wants to generate complete CI/CD workflows for Storybook deployment and testing.
---

# CI/CD Pipeline Generator Skill

## Overview

Generate production-ready CI/CD pipelines for Storybook with one command. Includes automated testing, visual regression, deployment, and PR previews.

## Generated Workflows

### GitHub Actions + Vercel

**.github/workflows/storybook.yml:**
```yaml
name: Storybook CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci
      - run: npm run build-storybook
      - run: npm run test-storybook

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  visual-regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4

      - run: npm ci
      - run: npm run chromatic
        env:
          CHROMATIC_PROJECT_TOKEN: ${{ secrets.CHROMATIC_TOKEN }}

  deploy:
    needs: [test, visual-regression]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4

      - run: npm ci
      - run: npm run build-storybook

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## Features

### Automated Testing
- Run interaction tests
- Run accessibility tests
- Generate coverage reports
- Fail PR on test failures

### Visual Regression (Chromatic)
- Capture screenshots of all stories
- Compare with baseline
- Flag visual changes
- Approve/reject in PR

### Deployment
- Auto-deploy main branch to production
- Deploy PR previews
- Comment with preview URL
- Rollback on failure

### Bundle Analysis
- Track bundle size over time
- Comment on PR with size changes
- Fail if bundle grows >10%

## Quick Setup

```bash
User: /setup-ci-cd

Detecting environment...
  ✓ Git repository found
  ✓ package.json detected
  ✓ GitHub Actions available

Select deployment target:
  [1] Vercel (Recommended)
  [2] Netlify
  [3] GitHub Pages
  [4] AWS S3

Select features:
  ☑ Automated testing
  ☑ Visual regression (Chromatic)
  ☑ Bundle size tracking
  ☑ PR preview comments
  ☐ Accessibility checks (already in tests)

Generating workflows...
  ✓ .github/workflows/storybook.yml
  ✓ .github/workflows/visual-regression.yml
  ✓ chromatic.config.js
  ✓ Updated package.json scripts

Setup environment secrets:
  1. Go to GitHub → Settings → Secrets
  2. Add: CHROMATIC_PROJECT_TOKEN
  3. Add: VERCEL_TOKEN
  4. Add: VERCEL_ORG_ID
  5. Add: VERCEL_PROJECT_ID

Next PR will trigger full pipeline ✓
```

## Summary

One-command CI/CD setup:
- GitHub Actions workflows
- Chromatic visual regression
- Auto-deployment
- PR previews

**Result:** Production-ready pipeline in 2 minutes.
