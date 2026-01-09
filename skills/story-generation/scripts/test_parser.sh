#!/usr/bin/env bash
# Test script for component parser and story generator

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_SAMPLE="${SCRIPT_DIR}/test_samples/Button.tsx"

echo "🧪 Testing Component Parser & Story Generator"
echo "=============================================="
echo ""

# Test 1: Component Parser
echo "📋 Test 1: Parse Component"
echo "File: ${TEST_SAMPLE}"
echo ""
python3 "${SCRIPT_DIR}/parse_component.py" "${TEST_SAMPLE}"
echo ""

# Test 2: Variant Detection
echo "🎨 Test 2: Detect Variants"
echo ""
python3 "${SCRIPT_DIR}/detect_variants.py" "${TEST_SAMPLE}"
echo ""

# Test 3: Story Generation (Full)
echo "📝 Test 3: Generate Story (Full Testing)"
echo ""
python3 "${SCRIPT_DIR}/generate_story.py" "${TEST_SAMPLE}" --level full --dry-run
echo ""

# Test 4: Story Generation (Basic)
echo "📝 Test 4: Generate Story (Basic)"
echo ""
python3 "${SCRIPT_DIR}/generate_story.py" "${TEST_SAMPLE}" --level basic --dry-run | head -30
echo ""
echo "... (truncated)"
echo ""

echo "✅ All tests completed successfully!"
echo ""
echo "To generate a real story file:"
echo "  python3 ${SCRIPT_DIR}/generate_story.py ${TEST_SAMPLE} --output Button.stories.tsx"
