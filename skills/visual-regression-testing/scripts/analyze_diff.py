#!/usr/bin/env python3
"""
AI-Powered Visual Regression Analysis

Analyzes visual diffs with context awareness to categorize changes as:
- IGNORE: Rendering noise (auto-pass)
- EXPECTED: Intentional design changes (auto-approve)
- WARNING: Significant changes requiring review
- ERROR: Clear regressions (block merge)
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("❌ Error: Required dependencies not installed")
    print("Run: pip install Pillow numpy")
    sys.exit(1)


class Category(Enum):
    """Change category classification"""

    IGNORE = "ignore"
    EXPECTED = "expected"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class VisualChange:
    """Represents a detected visual change"""

    change_type: str  # color, position, size, text
    element: str
    old_value: str
    new_value: str
    pixels_affected: int
    percentage: float
    category: Category
    reason: str
    evidence: str
    recommendation: str


@dataclass
class AnalysisContext:
    """Context for analysis"""

    component_name: str
    story_id: str
    recent_commits: List[Dict]
    design_tokens: Dict
    pr_description: Optional[str]
    baseline_path: str
    current_path: str


def get_recent_commits(days: int = 7) -> List[Dict]:
    """Get recent git commits for context"""
    try:
        cmd = [
            "git",
            "log",
            f"--since={days} days ago",
            "--pretty=format:%H|%an|%ae|%s|%ct",
            "--all",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            sha, author, email, message, timestamp = line.split("|")
            commits.append(
                {
                    "sha": sha,
                    "author": author,
                    "email": email,
                    "message": message,
                    "timestamp": int(timestamp),
                }
            )
        return commits
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def load_design_tokens() -> Dict:
    """Load design tokens from project"""
    token_paths = [
        "src/tokens/",
        "src/theme/",
        "src/styles/tokens/",
        "design-tokens.json",
    ]

    tokens = {}

    for path in token_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                # Load all JSON/TS files in directory
                for file in Path(path).rglob("*.json"):
                    try:
                        with open(file, "r") as f:
                            file_tokens = json.load(f)
                            tokens.update(file_tokens)
                    except (json.JSONDecodeError, IOError):
                        continue
            elif path.endswith(".json"):
                try:
                    with open(path, "r") as f:
                        tokens = json.load(f)
                        break
                except (json.JSONDecodeError, IOError):
                    continue

    return tokens


def check_token_match(old_value: str, new_value: str, tokens: Dict) -> Optional[Dict]:
    """Check if change matches a design token update"""
    # Flatten nested tokens
    flat_tokens = flatten_dict(tokens)

    # Look for tokens with old value that changed to new value
    for token_name, token_value in flat_tokens.items():
        if isinstance(token_value, dict):
            if token_value.get("value") == new_value:
                # Found new value, check if old value was previous
                return {
                    "token_name": token_name,
                    "old_value": old_value,
                    "new_value": new_value,
                }

    return None


def flatten_dict(d: Dict, parent_key: str = "", sep: str = ".") -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def calculate_pixel_diff(baseline_path: str, current_path: str) -> Tuple[int, float]:
    """Calculate pixel difference between images"""
    try:
        baseline = Image.open(baseline_path).convert("RGB")
        current = Image.open(current_path).convert("RGB")

        # Ensure same dimensions
        if baseline.size != current.size:
            raise ValueError("Image dimensions do not match")

        # Convert to numpy arrays
        baseline_arr = np.array(baseline)
        current_arr = np.array(current)

        # Calculate difference
        diff = np.abs(baseline_arr - current_arr)

        # Count changed pixels (with threshold)
        threshold = 10  # RGB difference threshold
        changed_pixels = np.sum(np.any(diff > threshold, axis=2))

        total_pixels = baseline.size[0] * baseline.size[1]
        percentage = (changed_pixels / total_pixels) * 100

        return changed_pixels, percentage
    except (IOError, ValueError) as e:
        raise RuntimeError(f"Error comparing images: {e}")


def categorize_change(
    change_type: str,
    old_value: str,
    new_value: str,
    pixels: int,
    percentage: float,
    context: AnalysisContext,
) -> Tuple[Category, str, str, str]:
    """Categorize a change based on type and context"""

    # IGNORE: Very small changes (likely rendering noise)
    if percentage < 0.1:
        return (
            Category.IGNORE,
            "Sub-pixel rendering variation or anti-aliasing",
            f"Only {pixels:,} pixels changed ({percentage:.2f}%)",
            "AUTO-APPROVE",
        )

    # Check design token match for color changes
    if change_type == "color":
        token_match = check_token_match(old_value, new_value, context.design_tokens)
        if token_match:
            return (
                Category.EXPECTED,
                f"Matches design token update: {token_match['token_name']}",
                f"Token value changed from {old_value} to {new_value}",
                "APPROVE - Design system update",
            )

    # Check commit messages
    relevant_commits = find_relevant_commits(
        change_type, old_value, new_value, context.recent_commits
    )

    if relevant_commits:
        commit = relevant_commits[0]
        return (
            Category.EXPECTED,
            "Change mentioned in recent commit",
            f"{commit['message']} ({commit['sha'][:7]})",
            "APPROVE - Mentioned in commit",
        )

    # Layout shifts are almost always errors
    if change_type == "position" and percentage > 1.0:
        return (
            Category.ERROR,
            "Layout shift detected without related code changes",
            f"{pixels:,} pixels shifted ({percentage:.2f}% of component)",
            "REJECT - Investigate layout regression",
        )

    # Significant changes without context = warning
    if percentage > 5.0:
        return (
            Category.WARNING,
            f"Significant {change_type} change detected",
            f"{pixels:,} pixels affected ({percentage:.2f}%)",
            "REVIEW - Verify change is intentional",
        )

    # Moderate changes = warning
    return (
        Category.WARNING,
        f"{change_type.capitalize()} change without design token update",
        f"{old_value} → {new_value} ({pixels:,} pixels)",
        "REVIEW - Consider updating design tokens",
    )


def find_relevant_commits(
    change_type: str, old_value: str, new_value: str, commits: List[Dict]
) -> List[Dict]:
    """Find commits that might relate to this change"""
    keywords = {
        "color": ["color", "theme", "palette", new_value.lower()],
        "position": ["layout", "position", "flexbox", "grid", "spacing"],
        "size": ["size", "width", "height", "dimensions"],
        "text": ["text", "content", "copy", "typography"],
    }

    relevant = []
    search_terms = keywords.get(change_type, [])

    for commit in commits:
        message_lower = commit["message"].lower()
        if any(term in message_lower for term in search_terms):
            relevant.append(commit)

    return relevant


def analyze_visual_diff(context: AnalysisContext) -> Dict:
    """Main analysis function"""

    # Calculate pixel difference
    try:
        pixels_changed, percentage = calculate_pixel_diff(
            context.baseline_path, context.current_path
        )
    except RuntimeError as e:
        return {"error": str(e), "success": False}

    # If no changes, return early
    if pixels_changed == 0:
        return {
            "success": True,
            "changes_detected": 0,
            "category": Category.IGNORE.value,
            "message": "No visual changes detected",
        }

    # Analyze the change
    # In a real implementation, we would detect change type by analyzing
    # which pixels changed (color vs position vs size)
    # For now, we'll use a simplified approach

    category, reason, evidence, recommendation = categorize_change(
        change_type="unknown",  # Would detect from pixel analysis
        old_value="",
        new_value="",
        pixels=pixels_changed,
        percentage=percentage,
        context=context,
    )

    return {
        "success": True,
        "changes_detected": pixels_changed,
        "percentage": percentage,
        "category": category.value,
        "reason": reason,
        "evidence": evidence,
        "recommendation": recommendation,
        "component": context.component_name,
        "story_id": context.story_id,
    }


def main():
    """CLI entry point"""
    if len(sys.argv) < 5:
        print(
            "Usage: analyze_diff.py <component_name> <story_id> <baseline_path> <current_path>"
        )
        sys.exit(1)

    component_name = sys.argv[1]
    story_id = sys.argv[2]
    baseline_path = sys.argv[3]
    current_path = sys.argv[4]

    # Gather context
    print(f"Analyzing visual diff for {component_name}/{story_id}...")
    print("Gathering context...")

    recent_commits = get_recent_commits(days=7)
    design_tokens = load_design_tokens()

    context = AnalysisContext(
        component_name=component_name,
        story_id=story_id,
        recent_commits=recent_commits,
        design_tokens=design_tokens,
        pr_description=None,
        baseline_path=baseline_path,
        current_path=current_path,
    )

    print(f"Found {len(recent_commits)} recent commits")
    print(f"Loaded {len(design_tokens)} design tokens")
    print()

    # Analyze
    result = analyze_visual_diff(context)

    if not result["success"]:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    # Print results
    print("📊 Analysis Results:")
    print(
        f"  Changes: {result['changes_detected']:,} pixels ({result.get('percentage', 0):.2f}%)"
    )
    print(f"  Category: {result['category'].upper()}")
    print(f"  Reason: {result['reason']}")
    print(f"  Evidence: {result['evidence']}")
    print(f"  Recommendation: {result['recommendation']}")
    print()

    # Exit code based on category
    category_exit_codes = {"ignore": 0, "expected": 0, "warning": 1, "error": 2}

    exit_code = category_exit_codes.get(result["category"], 1)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
