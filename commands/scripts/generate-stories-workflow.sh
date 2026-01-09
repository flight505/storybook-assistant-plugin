#!/usr/bin/env bash
# Generate Stories Workflow - Orchestrates component scanning and story generation
# This script integrates the component parser system with the /generate-stories command

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

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Parse command line arguments
SCAN_DIR="${1:-src}"
OUTPUT_FORMAT="${2:-human}"  # human or json

print_info "Scanning for components in: ${SCAN_DIR}"
echo ""

# Check if scan directory exists
if [ ! -d "${SCAN_DIR}" ]; then
    print_error "Directory not found: ${SCAN_DIR}"
    exit 1
fi

# Run component scanner
print_info "Running component scanner..."

# Capture both stdout and stderr, filter out status messages
SCAN_OUTPUT=$(python3 "${SCRIPTS_DIR}/scan_components.py" "${SCAN_DIR}" --json 2>&1)
SCAN_EXIT_CODE=$?

if [ $SCAN_EXIT_CODE -ne 0 ]; then
    print_error "Component scanning failed"
    echo "${SCAN_OUTPUT}"
    exit 1
fi

# Extract JSON from output (skip status messages that start with "Found" or "Successfully")
SCAN_RESULT=$(echo "${SCAN_OUTPUT}" | grep -v "^Found " | grep -v "^Successfully ")

# Parse JSON result
COMPONENT_COUNT=$(echo "${SCAN_RESULT}" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

if [ "${COMPONENT_COUNT}" = "0" ]; then
    print_warning "No components found in ${SCAN_DIR}"
    echo ""
    print_info "Suggestions:"
    echo "  • Check if your component files use standard extensions (.tsx, .jsx, .vue, .svelte)"
    echo "  • Ensure component names start with uppercase letter"
    echo "  • Try scanning a different directory: /generate-stories <directory>"
    exit 0
fi

print_success "Found ${COMPONENT_COUNT} component(s)"
echo ""

# Output component data for Claude to process
if [ "${OUTPUT_FORMAT}" = "json" ]; then
    # Output raw JSON for programmatic parsing
    echo "${SCAN_RESULT}"
else
    # Output human-readable format
    print_info "Components discovered:"
    echo ""

    # Parse and format component information
    echo "${SCAN_RESULT}" | python3 -c "
import sys
import json

try:
    components = json.load(sys.stdin)

    # Group by framework
    by_framework = {}
    for comp in components:
        framework = comp.get('framework', 'unknown')
        if framework not in by_framework:
            by_framework[framework] = []
        by_framework[framework].append(comp)

    # Display grouped components
    for framework, comps in sorted(by_framework.items()):
        print(f'\n{framework.upper()}:')
        for comp in comps:
            name = comp.get('name', 'Unknown')
            path = comp.get('file_path', '')
            props_count = len(comp.get('props', []))
            comp_type = comp.get('component_type', 'component')

            print(f'  • {name}')
            print(f'    Path: {path}')
            print(f'    Props: {props_count} • Type: {comp_type}')

            # Show detected variants if available
            variants = comp.get('detected_variants', [])
            if variants:
                variant_preview = ', '.join([v.get('name', '') for v in variants[:3]])
                if len(variants) > 3:
                    variant_preview += f' (+{len(variants) - 3} more)'
                print(f'    Variants: {variant_preview}')
            print()

except Exception as e:
    print(f'Error parsing component data: {e}', file=sys.stderr)
    sys.exit(1)
"

    # Store the JSON data in a temp file for later use
    TEMP_FILE=$(mktemp)
    echo "${SCAN_RESULT}" > "${TEMP_FILE}"
    echo "COMPONENT_DATA_FILE=${TEMP_FILE}"
fi

print_success "Component discovery complete"
echo ""
print_info "Ready for user selection via AskUserQuestion"
