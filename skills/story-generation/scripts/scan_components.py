#!/usr/bin/env python3
"""
Component scanner for finding all components in a project
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from parse_component import parse_component


class ComponentScanner:
    """Scan project for components"""

    # Default patterns to exclude
    EXCLUDE_PATTERNS = [
        "node_modules",
        ".git",
        "dist",
        "build",
        "coverage",
        ".next",
        ".nuxt",
        ".storybook",
        "__pycache__",
        ".pytest_cache",
        "test",
        "tests",
        "__tests__",
        "*.test.*",
        "*.spec.*",
        "*.stories.*",
    ]

    # Component file extensions
    COMPONENT_EXTENSIONS = [".tsx", ".jsx", ".vue", ".svelte", ".ts", ".js"]

    @staticmethod
    def scan(
        root_dir: str,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Scan directory for components

        Args:
            root_dir: Root directory to scan
            include_patterns: Additional patterns to include
            exclude_patterns: Additional patterns to exclude

        Returns:
            List of component metadata dicts
        """

        root_path = Path(root_dir).resolve()

        if not root_path.exists():
            print(f"Directory not found: {root_dir}")
            return []

        # Combine exclude patterns
        exclude = ComponentScanner.EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude.extend(exclude_patterns)

        # Find all component files
        component_files = []

        for ext in ComponentScanner.COMPONENT_EXTENSIONS:
            for file_path in root_path.rglob(f"*{ext}"):
                # Skip excluded patterns
                if ComponentScanner._should_exclude(file_path, exclude):
                    continue

                # Check if it looks like a component
                if ComponentScanner._is_component_file(file_path):
                    component_files.append(file_path)

        print(f"Found {len(component_files)} potential component files")

        # Parse each component
        components = []
        for file_path in component_files:
            try:
                metadata = parse_component(str(file_path))
                if metadata:
                    # Convert to dict
                    component_dict = {
                        "name": metadata.name,
                        "file_path": str(file_path.relative_to(root_path)),
                        "framework": metadata.framework,
                        "component_type": metadata.component_type,
                        "props_count": len(metadata.props),
                        "has_children": metadata.has_children,
                        "props": [
                            {
                                "name": p.name,
                                "type": p.type,
                                "required": p.required,
                            }
                            for p in metadata.props
                        ],
                    }
                    components.append(component_dict)
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
                continue

        print(f"Successfully parsed {len(components)} components")
        return components

    @staticmethod
    def _should_exclude(file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded"""
        file_str = str(file_path)

        for pattern in exclude_patterns:
            # Exact directory match
            if pattern in file_path.parts:
                return True

            # Wildcard pattern
            if "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(file_str, f"*{pattern}"):
                    return True

        return False

    @staticmethod
    def _is_component_file(file_path: Path) -> bool:
        """Check if file is likely a component"""

        # Must be a valid component extension
        if file_path.suffix not in ComponentScanner.COMPONENT_EXTENSIONS:
            return False

        # Component files usually start with uppercase
        filename = file_path.stem
        if filename[0].isupper():
            return True

        # Or are in a components directory
        if "component" in str(file_path).lower():
            return True

        # Or are named index (for directory-based components)
        if filename.lower() == "index":
            return True

        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Scan project for components")
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--exclude", action="append", help="Additional patterns to exclude"
    )

    args = parser.parse_args()

    # Scan for components
    components = ComponentScanner.scan(args.root_dir, exclude_patterns=args.exclude)

    if args.json:
        print(json.dumps(components, indent=2))
    else:
        print(f"\n📦 Found {len(components)} components:\n")

        # Group by framework
        by_framework = {}
        for comp in components:
            framework = comp["framework"]
            if framework not in by_framework:
                by_framework[framework] = []
            by_framework[framework].append(comp)

        for framework, comps in sorted(by_framework.items()):
            print(f"\n{framework.upper()}:")
            for comp in sorted(comps, key=lambda c: c["name"]):
                print(f"  • {comp['name']}")
                print(f"    {comp['file_path']}")
                print(f"    {comp['props_count']} props • {comp['component_type']}")


if __name__ == "__main__":
    main()
