#!/usr/bin/env bash
# Environment check for Storybook Assistant Plugin
# Checks: Node.js, npm, Claude API keys, OpenRouter (optional)

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Storybook Assistant - Environment Check${NC}\n"

# Track issues
ISSUES=()
WARNINGS=()

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 20 ]; then
        echo -e "${GREEN}✓${NC} Node.js: v$NODE_VERSION"
    else
        echo -e "${RED}✗${NC} Node.js: v$NODE_VERSION (requires >=20.0.0)"
        ISSUES+=("Node.js version too old. Please upgrade to v20 or higher.")
    fi
else
    echo -e "${RED}✗${NC} Node.js: not found"
    ISSUES+=("Node.js not installed. Install from: https://nodejs.org/")
fi

# Check npm version
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    NPM_MAJOR=$(echo $NPM_VERSION | cut -d. -f1)
    if [ "$NPM_MAJOR" -ge 10 ]; then
        echo -e "${GREEN}✓${NC} npm: v$NPM_VERSION"
    else
        echo -e "${YELLOW}⚠${NC} npm: v$NPM_VERSION (recommended >=10.0.0)"
        WARNINGS+=("npm version < 10. Consider upgrading: npm install -g npm@latest")
    fi
else
    echo -e "${RED}✗${NC} npm: not found"
    ISSUES+=("npm not installed.")
fi

# Check Claude API keys (prioritize CLAUDE_CODE_OAUTH_TOKEN)
CLAUDE_API_AVAILABLE=false

if [ ! -z "$CLAUDE_CODE_OAUTH_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Claude API: CLAUDE_CODE_OAUTH_TOKEN found"
    CLAUDE_API_AVAILABLE=true
elif [ ! -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} Claude API: ANTHROPIC_API_KEY found"
    CLAUDE_API_AVAILABLE=true
else
    echo -e "${RED}✗${NC} Claude API: No API key found"
    ISSUES+=("Claude API key required. Set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY")
fi

# Check OpenRouter API key (optional for visual generation)
if [ ! -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} OpenRouter API: Available (visual generation enabled)"
else
    echo -e "${YELLOW}ℹ${NC} OpenRouter API: Not configured (visual generation disabled)"
    echo -e "   ${YELLOW}└─${NC} Visual features (style guides, mockups, diagrams) will be skipped"
    echo -e "   ${YELLOW}└─${NC} To enable: Set OPENROUTER_API_KEY from https://openrouter.ai/keys"
fi

# Check for existing Storybook installation
if [ -d ".storybook" ]; then
    echo -e "${BLUE}ℹ${NC} Existing Storybook detected in project"
    if [ -f "package.json" ]; then
        if grep -q "\"storybook\":" package.json; then
            STORYBOOK_VERSION=$(grep "\"storybook\":" package.json | sed 's/.*: "[\^~]*//' | sed 's/".*//')
            echo -e "   ${BLUE}└─${NC} Version: $STORYBOOK_VERSION"

            # Check if it's Storybook 9+
            MAJOR_VERSION=$(echo $STORYBOOK_VERSION | cut -d. -f1)
            if [ "$MAJOR_VERSION" -ge 9 ]; then
                echo -e "   ${GREEN}└─${NC} Storybook 9+ detected (SOTA version)"
            else
                echo -e "   ${YELLOW}└─${NC} Older version detected. Consider migration with /migrate-storybook"
            fi
        fi
    fi
else
    echo -e "${BLUE}ℹ${NC} No Storybook installation detected (use /setup-storybook to initialize)"
fi

# Summary
echo ""
if [ ${#ISSUES[@]} -eq 0 ]; then
    if [ ${#WARNINGS[@]} -eq 0 ]; then
        echo -e "${GREEN}✅ Environment ready for Storybook Assistant${NC}"
    else
        echo -e "${YELLOW}⚠️  Environment ready with warnings:${NC}"
        for warning in "${WARNINGS[@]}"; do
            echo -e "   ${YELLOW}•${NC} $warning"
        done
    fi

    # Show quick start
    echo ""
    echo -e "${BLUE}🚀 Quick Start:${NC}"
    echo -e "   ${BLUE}1.${NC} Run: ${GREEN}/setup-storybook${NC} - Initialize Storybook 9 in your project"
    echo -e "   ${BLUE}2.${NC} Run: ${GREEN}/generate-stories${NC} - Generate stories for existing components"
    echo -e "   ${BLUE}3.${NC} Run: ${GREEN}/create-component${NC} - Scaffold new component with tests"

    exit 0
else
    echo -e "${RED}❌ Environment issues found:${NC}"
    for issue in "${ISSUES[@]}"; do
        echo -e "   ${RED}•${NC} $issue"
    done

    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  Warnings:${NC}"
        for warning in "${WARNINGS[@]}"; do
            echo -e "   ${YELLOW}•${NC} $warning"
        done
    fi

    echo ""
    echo -e "${BLUE}ℹ${NC} Please resolve issues before using Storybook Assistant"
    exit 1
fi
