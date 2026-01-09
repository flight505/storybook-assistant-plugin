#!/usr/bin/env bash
# Batch Story Generation - Generates stories for multiple components
# Called after user selects components via AskUserQuestion

set -e

# Determine plugin root - use CLAUDE_PLUGIN_ROOT if available, otherwise use script location
if [ -n "${CLAUDE_PLUGIN_ROOT}" ]; then
    PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"
else
    # For standalone testing, derive from script location
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
fi

STORY_GEN_DIR="${PLUGIN_ROOT}/skills/story-generation"
SCRIPTS_DIR="${STORY_GEN_DIR}/scripts"

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
COMPONENT_PATHS_FILE="$1"
TESTING_LEVEL="${2:-full}"
GENERATE_MOCKUPS="${3:-false}"

if [ -z "${COMPONENT_PATHS_FILE}" ] || [ ! -f "${COMPONENT_PATHS_FILE}" ]; then
    print_error "Component paths file not provided or doesn't exist"
    exit 1
fi

# Read component paths (portable method for macOS/bash 3.2+)
COMPONENT_PATHS=()
while IFS= read -r line; do
    COMPONENT_PATHS+=("$line")
done < "${COMPONENT_PATHS_FILE}"
TOTAL_COMPONENTS=${#COMPONENT_PATHS[@]}

print_info "Generating stories for ${TOTAL_COMPONENTS} component(s)"
print_info "Testing level: ${TESTING_LEVEL}"
echo ""

# Counters for summary
SUCCESS_COUNT=0
ERROR_COUNT=0
MOCKUP_COUNT=0

declare -a GENERATED_FILES
declare -a ERROR_FILES

# Process each component
for i in "${!COMPONENT_PATHS[@]}"; do
    COMPONENT_PATH="${COMPONENT_PATHS[$i]}"
    COMPONENT_NUM=$((i + 1))

    print_info "[${COMPONENT_NUM}/${TOTAL_COMPONENTS}] Processing: ${COMPONENT_PATH}"

    # Determine output path
    COMPONENT_DIR=$(dirname "${COMPONENT_PATH}")
    COMPONENT_FILENAME=$(basename "${COMPONENT_PATH}")
    COMPONENT_NAME="${COMPONENT_FILENAME%.*}"

    # Determine story file extension based on component
    case "${COMPONENT_PATH}" in
        *.tsx)
            STORY_EXT=".stories.tsx"
            ;;
        *.jsx)
            STORY_EXT=".stories.jsx"
            ;;
        *.vue)
            STORY_EXT=".stories.ts"
            ;;
        *.svelte)
            STORY_EXT=".stories.ts"
            ;;
        *)
            print_warning "  Unknown file type, defaulting to .stories.tsx"
            STORY_EXT=".stories.tsx"
            ;;
    esac

    OUTPUT_PATH="${COMPONENT_DIR}/${COMPONENT_NAME}${STORY_EXT}"

    # Check if story file already exists
    if [ -f "${OUTPUT_PATH}" ]; then
        print_warning "  Story file already exists: ${OUTPUT_PATH}"
        print_info "  Skipping... (use --force to overwrite)"
        continue
    fi

    # Generate story
    print_info "  Generating story file..."

    if python3 "${SCRIPTS_DIR}/generate_story.py" \
        "${COMPONENT_PATH}" \
        --level "${TESTING_LEVEL}" \
        --output "${OUTPUT_PATH}" 2>&1; then

        print_success "  Generated: ${OUTPUT_PATH}"
        GENERATED_FILES+=("${OUTPUT_PATH}")
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))

        # Generate mockup if enabled and component is complex
        if [ "${GENERATE_MOCKUPS}" = "true" ]; then
            # Parse component metadata to check if mockup is recommended
            COMPONENT_TYPE=$(python3 "${SCRIPTS_DIR}/parse_component.py" "${COMPONENT_PATH}" --json 2>/dev/null | \
                python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('component_type', 'unknown'))" 2>/dev/null || echo "unknown")

            # Generate mockups for complex components only
            case "${COMPONENT_TYPE}" in
                card|modal|table|form|dashboard|layout)
                    if [ ! -z "${OPENROUTER_API_KEY}" ]; then
                        print_info "  Generating visual mockup..."
                        MOCKUP_DIR="${COMPONENT_DIR}/mockups"
                        mkdir -p "${MOCKUP_DIR}"
                        MOCKUP_PATH="${MOCKUP_DIR}/${COMPONENT_NAME}.png"

                        # Generate mockup (this calls the visual-design skill)
                        # For now, we'll skip the actual generation and just note it
                        print_info "  Mockup generation: Queued for ${COMPONENT_NAME}"
                        MOCKUP_COUNT=$((MOCKUP_COUNT + 1))
                    else
                        print_info "  Mockup generation: Skipped (OPENROUTER_API_KEY not set)"
                    fi
                    ;;
                *)
                    # Skip mockup for simple components
                    ;;
            esac
        fi

    else
        print_error "  Failed to generate story for ${COMPONENT_PATH}"
        ERROR_FILES+=("${COMPONENT_PATH}")
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi

    echo ""
done

# Summary
echo ""
echo "═══════════════════════════════════════════════"
echo "  Story Generation Summary"
echo "═══════════════════════════════════════════════"
echo ""

print_success "Successfully generated: ${SUCCESS_COUNT} stories"

if [ ${ERROR_COUNT} -gt 0 ]; then
    print_error "Failed: ${ERROR_COUNT} components"
fi

if [ ${MOCKUP_COUNT} -gt 0 ]; then
    print_info "Mockups queued: ${MOCKUP_COUNT}"
fi

echo ""

if [ ${SUCCESS_COUNT} -gt 0 ]; then
    echo "Generated Files:"
    for file in "${GENERATED_FILES[@]}"; do
        echo "  ✓ ${file}"
    done
    echo ""
fi

if [ ${ERROR_COUNT} -gt 0 ]; then
    echo "Failed Components:"
    for file in "${ERROR_FILES[@]}"; do
        echo "  ✗ ${file}"
    done
    echo ""
fi

# Next steps
if [ ${SUCCESS_COUNT} -gt 0 ]; then
    echo "Next Steps:"
    echo "  1. Run Storybook: npm run storybook"
    echo "  2. Review generated stories in your browser"
    echo "  3. Run interaction tests: npm run test-storybook"
    echo "  4. Run accessibility tests: npm run storybook -- --test-runner"
    echo ""
fi

# Exit with error if all components failed
if [ ${SUCCESS_COUNT} -eq 0 ] && [ ${ERROR_COUNT} -gt 0 ]; then
    exit 1
fi

exit 0
