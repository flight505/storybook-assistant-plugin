#!/usr/bin/env python3
"""
Variant detection for component props
Analyzes prop types and generates intelligent story variants
"""

import re
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class Variant:
    name: str
    description: str
    args: Dict[str, Any]
    priority: int = 1  # 1=high, 2=medium, 3=low


class VariantDetector:
    """Detect variants from component props"""

    # Common variant prop names and their values
    VARIANT_PATTERNS = {
        "variant": [
            "primary",
            "secondary",
            "outline",
            "ghost",
            "link",
            "danger",
            "success",
            "warning",
        ],
        "color": ["primary", "secondary", "success", "warning", "danger", "info"],
        "size": ["small", "medium", "large", "xs", "sm", "md", "lg", "xl"],
        "type": ["button", "submit", "reset", "text", "email", "password", "number"],
        "appearance": ["filled", "outline", "ghost", "link"],
        "intent": ["primary", "success", "warning", "danger"],
    }

    # Size-related prop names
    SIZE_PROPS = ["size", "fontSize", "width", "height"]

    # Boolean state props
    STATE_PROPS = [
        "disabled",
        "loading",
        "active",
        "selected",
        "checked",
        "error",
        "readonly",
    ]

    @staticmethod
    def detect_variants(component_metadata: Dict[str, Any]) -> List[Variant]:
        """Detect all possible variants from component props"""
        variants = []
        props = component_metadata.get("props", [])
        component_type = component_metadata.get("component_type", "other")

        # 1. Detect enum/union type variants
        variants.extend(VariantDetector._detect_enum_variants(props))

        # 2. Detect size variants
        variants.extend(VariantDetector._detect_size_variants(props))

        # 3. Detect state variants
        variants.extend(VariantDetector._detect_state_variants(props))

        # 4. Detect component-type specific variants
        variants.extend(
            VariantDetector._detect_type_specific_variants(component_type, props)
        )

        # 5. Add default variant if no variants detected
        if not variants:
            variants.append(
                Variant(
                    name="Default",
                    description="Default component state",
                    args={},
                    priority=1,
                )
            )

        # Sort by priority
        variants.sort(key=lambda v: v.priority)

        return variants

    @staticmethod
    def _detect_enum_variants(props: List[Dict[str, Any]]) -> List[Variant]:
        """Detect variants from enum/union types"""
        variants = []

        for prop in props:
            prop_name = prop["name"]
            prop_type = prop["type"]

            # Check if prop name matches known variant patterns
            if prop_name in VariantDetector.VARIANT_PATTERNS:
                expected_values = VariantDetector.VARIANT_PATTERNS[prop_name]

                # Parse union type: 'primary' | 'secondary' | 'outline'
                union_values = VariantDetector._parse_union_type(prop_type)

                if union_values:
                    for value in union_values:
                        # Only create variant if value is in expected list or if we don't have a list
                        if not expected_values or value in expected_values:
                            variants.append(
                                Variant(
                                    name=value.capitalize(),
                                    description=f"{prop_name}: {value}",
                                    args={prop_name: value},
                                    priority=1,
                                )
                            )

        return variants

    @staticmethod
    def _detect_size_variants(props: List[Dict[str, Any]]) -> List[Variant]:
        """Detect size-related variants"""
        variants = []

        for prop in props:
            prop_name = prop["name"]
            prop_type = prop["type"]

            if prop_name.lower() in ["size", "fontsize"]:
                union_values = VariantDetector._parse_union_type(prop_type)

                if union_values:
                    # Create small and large variants (skip medium/default)
                    for value in union_values:
                        if value.lower() in ["small", "sm", "xs"]:
                            variants.append(
                                Variant(
                                    name="Small",
                                    description="Small size variant",
                                    args={prop_name: value},
                                    priority=2,
                                )
                            )
                        elif value.lower() in ["large", "lg", "xl"]:
                            variants.append(
                                Variant(
                                    name="Large",
                                    description="Large size variant",
                                    args={prop_name: value},
                                    priority=2,
                                )
                            )

        return variants

    @staticmethod
    def _detect_state_variants(props: List[Dict[str, Any]]) -> List[Variant]:
        """Detect boolean state variants"""
        variants = []

        for prop in props:
            prop_name = prop["name"]
            prop_type = prop["type"]

            # Check if it's a boolean type
            if "boolean" in prop_type.lower():
                if prop_name.lower() in VariantDetector.STATE_PROPS:
                    variants.append(
                        Variant(
                            name=prop_name.capitalize(),
                            description=f"{prop_name} state",
                            args={prop_name: True},
                            priority=2,
                        )
                    )

        return variants

    @staticmethod
    def _detect_type_specific_variants(
        component_type: str, props: List[Dict[str, Any]]
    ) -> List[Variant]:
        """Detect variants specific to component type"""
        variants = []

        if component_type == "button":
            # Check for icon prop
            has_icon = any(
                p["name"].lower() in ["icon", "lefticon", "righticon"] for p in props
            )
            if has_icon:
                variants.append(
                    Variant(
                        name="WithIcon",
                        description="Button with icon",
                        args={},
                        priority=3,
                    )
                )

        elif component_type == "input":
            # Error state
            has_error = any(
                p["name"].lower() in ["error", "iserror", "haserror"] for p in props
            )
            if has_error:
                variants.append(
                    Variant(
                        name="WithError",
                        description="Input with error state",
                        args={"error": "This field is required"},
                        priority=2,
                    )
                )

        elif component_type == "modal":
            variants.append(
                Variant(
                    name="Open",
                    description="Modal in open state",
                    args={"isOpen": True},
                    priority=1,
                )
            )

        elif component_type == "table":
            variants.append(
                Variant(
                    name="WithData",
                    description="Table with sample data",
                    args={},
                    priority=1,
                )
            )
            variants.append(
                Variant(
                    name="Empty", description="Table with no data", args={}, priority=2
                )
            )

        return variants

    @staticmethod
    def _parse_union_type(type_str: str) -> List[str]:
        """Parse union type string: 'primary' | 'secondary' | 'outline'"""
        # Remove quotes and split by |
        values = []

        # Pattern: 'value' or "value"
        matches = re.findall(r'["\']([^"\']+)["\']', type_str)

        if matches:
            values = matches
        else:
            # Try without quotes (TypeScript enums)
            if "|" in type_str:
                parts = type_str.split("|")
                values = [p.strip() for p in parts if p.strip()]

        return values


def detect_variants_from_file(file_path: str) -> List[Variant]:
    """Parse component file and detect variants"""
    from parse_component import parse_component

    metadata = parse_component(file_path)
    if not metadata:
        return []

    # Convert to dict
    metadata_dict = {
        "name": metadata.name,
        "component_type": metadata.component_type,
        "props": [
            {
                "name": p.name,
                "type": p.type,
                "required": p.required,
                "default_value": p.default_value,
            }
            for p in metadata.props
        ],
    }

    return VariantDetector.detect_variants(metadata_dict)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Detect component variants from props")
    parser.add_argument("file_path", help="Path to component file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    variants = detect_variants_from_file(args.file_path)

    if args.json:
        data = [asdict(v) for v in variants]
        print(json.dumps(data, indent=2))
    else:
        print(f"Detected {len(variants)} variants:")
        for i, variant in enumerate(variants, 1):
            print(f"\n{i}. {variant.name}")
            print(f"   Description: {variant.description}")
            print(f"   Args: {variant.args}")
            print(f"   Priority: {variant.priority}")


if __name__ == "__main__":
    main()
