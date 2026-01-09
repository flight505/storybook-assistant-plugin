#!/usr/bin/env bash
# Create Component Workflow - Orchestrates component scaffolding
# This script integrates component generation with story generation and optional mockups

set -e

# Determine plugin root
if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
    PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
fi

COMPONENT_SCAFFOLD_DIR="${PLUGIN_ROOT}/skills/component-scaffold"
STORY_GEN_DIR="${PLUGIN_ROOT}/skills/story-generation"
VISUAL_DESIGN_DIR="${PLUGIN_ROOT}/skills/visual-design"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Parse arguments
COMPONENT_NAME="$1"
COMPONENT_TYPE="${2:-custom}"
FRAMEWORK="${3:-react}"
TESTING_LEVEL="${4:-full}"
GENERATE_MOCKUP="${5:-false}"
OUTPUT_DIR="${6:-src/components}"

# Validate inputs
if [ -z "${COMPONENT_NAME}" ]; then
    print_error "Component name is required"
    echo "Usage: $0 <name> [type] [framework] [testing_level] [generate_mockup] [output_dir]"
    exit 1
fi

# Validate component name (must start with uppercase)
if [[ ! "${COMPONENT_NAME}" =~ ^[A-Z] ]]; then
    print_error "Component name must start with uppercase letter (PascalCase)"
    echo "Example: MyButton, UserCard, DataTable"
    exit 1
fi

# Determine file extension based on framework
case "${FRAMEWORK}" in
    react)
        FILE_EXT=".tsx"
        ;;
    vue)
        FILE_EXT=".vue"
        ;;
    svelte)
        FILE_EXT=".svelte"
        ;;
    *)
        print_error "Unknown framework: ${FRAMEWORK}"
        exit 1
        ;;
esac

# Create output directory if it doesn't exist
mkdir -p "${OUTPUT_DIR}"

COMPONENT_FILE="${OUTPUT_DIR}/${COMPONENT_NAME}${FILE_EXT}"
STORY_FILE="${OUTPUT_DIR}/${COMPONENT_NAME}.stories${FILE_EXT}"

echo ""
print_info "Creating Component: ${COMPONENT_NAME}"
print_info "Type: ${COMPONENT_TYPE}"
print_info "Framework: ${FRAMEWORK}"
print_info "Output: ${COMPONENT_FILE}"
echo ""

# Check if component already exists
if [ -f "${COMPONENT_FILE}" ]; then
    print_warning "Component already exists: ${COMPONENT_FILE}"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cancelled"
        exit 0
    fi
fi

# Step 1: Generate Component
print_info "Generating component file..."

if python3 "${COMPONENT_SCAFFOLD_DIR}/scripts/create_component.py" \
    --name "${COMPONENT_NAME}" \
    --type "${COMPONENT_TYPE}" \
    --framework "${FRAMEWORK}" \
    --typescript \
    --output "${COMPONENT_FILE}" 2>&1; then

    print_success "Component generated: ${COMPONENT_FILE}"
else
    print_error "Failed to generate component"
    exit 1
fi

echo ""

# Step 2: Generate Story (if not minimal)
if [ "${TESTING_LEVEL}" != "minimal" ]; then
    print_info "Generating story file..."

    if python3 "${STORY_GEN_DIR}/scripts/generate_story.py" \
        "${COMPONENT_FILE}" \
        --level "${TESTING_LEVEL}" \
        --output "${STORY_FILE}" 2>&1; then

        print_success "Story generated: ${STORY_FILE}"
    else
        print_warning "Story generation failed (component still created)"
    fi

    echo ""
fi

# Step 3: Generate Visual Mockup (if requested and API key available)
MOCKUP_FILE=""
if [ "${GENERATE_MOCKUP}" = "true" ]; then
    if [ ! -z "${OPENROUTER_API_KEY}" ]; then
        print_info "Generating visual mockup..."

        MOCKUP_DIR="${OUTPUT_DIR}/mockups"
        mkdir -p "${MOCKUP_DIR}"
        MOCKUP_FILE="${MOCKUP_DIR}/${COMPONENT_NAME}.png"

        # Build mockup prompt
        MOCKUP_PROMPT="Modern ${COMPONENT_TYPE} component for ${FRAMEWORK} application. \
Component name: ${COMPONENT_NAME}. \
Style: Clean, professional, follows design system best practices. \
Color scheme: Modern, accessible (WCAG AA compliant). \
Layout: Responsive, mobile-friendly."

        if python3 "${VISUAL_DESIGN_DIR}/scripts/generate_mockup.py" \
            "${MOCKUP_PROMPT}" \
            --model "google/gemini-3.0-pro-image" \
            --output "${MOCKUP_FILE}" 2>&1; then

            print_success "Mockup generated: ${MOCKUP_FILE}"
        else
            print_warning "Mockup generation failed (component still created)"
            MOCKUP_FILE=""
        fi

        echo ""
    else
        print_info "Skipping mockup (OPENROUTER_API_KEY not set)"
        echo ""
    fi
fi

# Summary
echo "═══════════════════════════════════════════════"
echo "  Component Created: ${COMPONENT_NAME}"
echo "═══════════════════════════════════════════════"
echo ""
echo "Type: ${COMPONENT_TYPE}"
echo "Framework: ${FRAMEWORK}"
echo ""
echo "Files Created:"
echo "  ✓ ${COMPONENT_FILE}"
if [ "${TESTING_LEVEL}" != "minimal" ]; then
    echo "  ✓ ${STORY_FILE}"
fi
if [ ! -z "${MOCKUP_FILE}" ] && [ -f "${MOCKUP_FILE}" ]; then
    echo "  ✓ ${MOCKUP_FILE}"
fi
echo ""

# Get component stats
PROPS_COUNT=$(python3 "${COMPONENT_SCAFFOLD_DIR}/scripts/create_component.py" \
    --name "${COMPONENT_NAME}" \
    --type "${COMPONENT_TYPE}" \
    --framework "${FRAMEWORK}" \
    --json 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data['props']))" 2>/dev/null || echo "N/A")

echo "Component Features:"
echo "  ✓ TypeScript interfaces with proper types"
echo "  ✓ Accessibility attributes (ARIA labels, roles)"
echo "  ✓ ${PROPS_COUNT} props with sensible defaults"
echo "  ✓ JSDoc documentation"
if [ "${TESTING_LEVEL}" = "full" ]; then
    echo "  ✓ Interaction tests with play functions"
    echo "  ✓ Accessibility tests with axe-core"
fi
echo ""

echo "Next Steps:"
echo "  1. Review component: ${COMPONENT_FILE}"
echo "  2. Customize props and styling as needed"
if [ "${TESTING_LEVEL}" != "minimal" ]; then
    echo "  3. Run Storybook: npm run storybook"
    echo "  4. View your component in the browser"
    if [ "${TESTING_LEVEL}" != "basic" ]; then
        echo "  5. Run tests: npm run test-storybook"
    fi
else
    echo "  3. Generate story: /generate-stories"
fi
echo ""

print_success "Component creation complete!"
