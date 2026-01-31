#!/usr/bin/env python3
"""
Story generation orchestrator
Combines component parser, variant detector, and templates to generate stories
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import local modules
from parse_component import parse_component, ComponentMetadata, PropDefinition
from detect_variants import VariantDetector, Variant


class StoryGenerator:
    """Generate Storybook stories from component metadata"""

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

    # Component type to interaction test mapping
    INTERACTION_TESTS = {
        "button": """
    const button = canvas.getByRole('button');
    await expect(button).toBeInTheDocument();
    await userEvent.click(button);
    if (args.onClick) {
      await expect(args.onClick).toHaveBeenCalled();
    }
    await expect(button).not.toBeDisabled();
        """,
        "input": """
    const input = canvas.getByRole('textbox');
    await expect(input).toBeInTheDocument();
    await userEvent.type(input, 'Test input');
    await expect(input).toHaveValue('Test input');
        """,
        "checkbox": """
    const checkbox = canvas.getByRole('checkbox');
    await expect(checkbox).toBeInTheDocument();
    await userEvent.click(checkbox);
    await expect(checkbox).toBeChecked();
        """,
        "select": """
    const select = canvas.getByRole('combobox');
    await expect(select).toBeInTheDocument();
    await userEvent.selectOptions(select, 'option1');
        """,
    }

    # Component type to a11y rules mapping
    A11Y_RULES = {
        "button": [
            "{ id: 'button-name', enabled: true }",
            "{ id: 'color-contrast', enabled: true }",
        ],
        "input": [
            "{ id: 'label', enabled: true }",
            "{ id: 'color-contrast', enabled: true }",
        ],
        "modal": [
            "{ id: 'aria-dialog-name', enabled: true }",
            "{ id: 'focus-trap', enabled: true }",
        ],
    }

    # Component type to a11y test code mapping
    A11Y_TEST_CODE = {
        "button": """
    const button = canvas.getByRole('button');
    button.focus();
    await expect(button).toHaveFocus();
    await userEvent.keyboard('{Enter}');
        """,
        "input": """
    const input = canvas.getByRole('textbox');
    await expect(input).toHaveAccessibleName();
    input.focus();
    await expect(input).toHaveFocus();
        """,
    }

    @staticmethod
    def generate_story(
        component_path: str,
        testing_level: str = "full",
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate story file for component

        Args:
            component_path: Path to component file
            testing_level: 'full', 'standard', 'basic', or 'minimal'
            output_path: Optional custom output path

        Returns:
            Generated story content as string
        """

        # Parse component
        metadata = parse_component(component_path)
        if not metadata:
            print(f"Failed to parse component: {component_path}", file=sys.stderr)
            return None

        # Detect variants
        metadata_dict = StoryGenerator._metadata_to_dict(metadata)
        variants = VariantDetector.detect_variants(metadata_dict)

        # Generate story content
        story_content = StoryGenerator._generate_story_content(
            metadata, variants, testing_level
        )

        # Write to file if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(story_content)
            print(f"✅ Story generated: {output_file}")

        return story_content

    @staticmethod
    def _metadata_to_dict(metadata: ComponentMetadata) -> Dict[str, Any]:
        """Convert ComponentMetadata to dict for variant detection"""
        return {
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

    @staticmethod
    def _generate_story_content(
        metadata: ComponentMetadata, variants: List[Variant], testing_level: str
    ) -> str:
        """Generate story file content from template"""

        # Select template based on framework and testing level
        template_name = f"{metadata.framework}-{testing_level}.template"
        template_path = StoryGenerator.TEMPLATE_DIR / template_name

        # Fallback to basic template if specific level not found
        if not template_path.exists():
            template_path = (
                StoryGenerator.TEMPLATE_DIR / f"{metadata.framework}-basic.template"
            )

        if not template_path.exists():
            print(f"Template not found: {template_path}", file=sys.stderr)
            return ""

        # Load template
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()

        # Generate story title (Components/ComponentName)
        story_title = f"Components/{metadata.name}"

        # Generate argTypes
        arg_types = StoryGenerator._generate_arg_types(metadata.props)

        # Generate variant stories
        variant_stories = StoryGenerator._generate_variant_stories(metadata, variants)

        # Generate default args
        default_args = StoryGenerator._generate_default_args(metadata)

        # Generate interaction test code
        interaction_test = StoryGenerator.INTERACTION_TESTS.get(
            metadata.component_type, "// Component-specific interaction test"
        )

        # Generate a11y rules
        a11y_rules = ",\n          ".join(
            StoryGenerator.A11Y_RULES.get(
                metadata.component_type, ["{ id: 'color-contrast', enabled: true }"]
            )
        )

        # Generate a11y test code
        a11y_test = StoryGenerator.A11Y_TEST_CODE.get(
            metadata.component_type, "// Component-specific accessibility test"
        )

        # Replace template variables
        story_content = template.replace("{{COMPONENT_NAME}}", metadata.name)
        story_content = story_content.replace("{{STORY_TITLE}}", story_title)
        story_content = story_content.replace("{{ARG_TYPES}}", arg_types)
        story_content = story_content.replace("{{VARIANT_STORIES}}", variant_stories)
        story_content = story_content.replace("{{DEFAULT_ARGS}}", default_args)
        story_content = story_content.replace(
            "{{INTERACTION_TEST_CODE}}", interaction_test.strip()
        )
        story_content = story_content.replace("{{A11Y_RULES}}", a11y_rules)
        story_content = story_content.replace("{{A11Y_TEST_CODE}}", a11y_test.strip())

        return story_content

    @staticmethod
    def _generate_arg_types(props: List[PropDefinition]) -> str:
        """Generate argTypes configuration"""
        arg_types = []

        for prop in props:
            # Skip children
            if prop.name == "children":
                continue

            # Determine control type
            control = StoryGenerator._infer_control_type(prop)

            if control:
                arg_types.append(f"    {prop.name}: {control},")

        return "\n".join(arg_types)

    @staticmethod
    def _infer_control_type(prop: PropDefinition) -> Optional[str]:
        """
        Infer Storybook 10 control type from prop type.

        Storybook 10 argTypes syntax:
        - Boolean: { control: 'boolean' }
        - Number: { control: 'number' } or { control: { type: 'number', min: 0, max: 100, step: 1 } }
        - Range: { control: { type: 'range', min: 0, max: 100, step: 1 } }
        - Text: { control: 'text' }
        - Color: { control: 'color' }
        - Date: { control: 'date' }
        - Object: { control: 'object' }
        - File: { control: { type: 'file', accept: '.png' } }
        - Enum (select): { options: ['a', 'b'], control: { type: 'select' } }
        - Enum (radio): { options: ['a', 'b'], control: { type: 'radio' } }
        - Enum (inline-radio): { options: ['a', 'b'], control: { type: 'inline-radio' } }
        - Enum (check): { options: ['a', 'b'], control: { type: 'check' } }
        - Enum (inline-check): { options: ['a', 'b'], control: { type: 'inline-check' } }
        - Enum (multi-select): { options: ['a', 'b'], control: { type: 'multi-select' } }
        - Action: { action: 'clicked' }
        """
        prop_type = prop.type.lower()
        prop_name = prop.name.lower()

        # Boolean
        if "boolean" in prop_type:
            return "{ control: 'boolean' }"

        # Number - check for range hints
        if "number" in prop_type:
            # Use range slider for opacity, progress, percentage-like props
            if any(
                hint in prop_name
                for hint in ["opacity", "progress", "percent", "ratio"]
            ):
                return "{ control: { type: 'range', min: 0, max: 1, step: 0.1 } }"
            # Use range for size/dimension props
            if any(
                hint in prop_name
                for hint in ["size", "width", "height", "padding", "margin", "gap"]
            ):
                return "{ control: { type: 'range', min: 0, max: 100, step: 1 } }"
            return "{ control: 'number' }"

        # Color - match by prop name pattern (background|color)
        if any(
            hint in prop_name
            for hint in ["color", "background", "bg", "fill", "stroke"]
        ):
            return "{ control: 'color' }"

        # Date - match by prop name pattern (Date$)
        if (
            prop_name.endswith("date")
            or prop_name.endswith("time")
            or "timestamp" in prop_name
        ):
            return "{ control: 'date' }"

        # Object/Array types
        if "object" in prop_type or "record" in prop_type or "{" in prop.type:
            return "{ control: 'object' }"
        if "array" in prop_type or "[]" in prop.type:
            return "{ control: 'object' }"

        # File input
        if "file" in prop_type or prop_name in ["file", "files", "src", "source"]:
            if "image" in prop_name or "avatar" in prop_name or "photo" in prop_name:
                return "{ control: { type: 'file', accept: 'image/*' } }"
            return "{ control: 'file' }"

        # String with union (enum) - Storybook 10 syntax: options at top level
        if "|" in prop.type and "'" in prop.type:
            matches = re.findall(r"'([^']+)'", prop.type)
            if matches:
                options_str = ", ".join([f"'{opt}'" for opt in matches])
                # Use radio for 2-4 options, select for more
                if len(matches) <= 4:
                    return (
                        f"{{ options: [{options_str}], control: {{ type: 'radio' }} }}"
                    )
                else:
                    return (
                        f"{{ options: [{options_str}], control: {{ type: 'select' }} }}"
                    )

        # Function/callback - use action
        if "function" in prop_type or "=>" in prop_type or prop_name.startswith("on"):
            return f"{{ action: '{prop.name}' }}"

        # String (text) - default for string types
        if "string" in prop_type:
            return "{ control: 'text' }"

        # ReactNode/ReactElement - disable control (too complex)
        if "react" in prop_type or "node" in prop_type or "element" in prop_type:
            return "{ control: false }"

        return None

    @staticmethod
    def _generate_variant_stories(
        metadata: ComponentMetadata, variants: List[Variant]
    ) -> str:
        """Generate variant story exports"""
        stories = []

        for variant in variants:
            # Generate args
            args = []
            for key, value in variant.args.items():
                if isinstance(value, str):
                    args.append(f"    {key}: '{value}',")
                elif isinstance(value, bool):
                    args.append(f"    {key}: {str(value).lower()},")
                else:
                    args.append(f"    {key}: {value},")

            # Add children for components that need it
            if metadata.has_children and "children" not in variant.args:
                args.append(f"    children: '{metadata.name}',")

            args_str = "\n".join(args)

            story = f"""
export const {variant.name}: Story = {{
  args: {{
{args_str}
  }},
}};
"""
            stories.append(story)

        return "\n".join(stories)

    @staticmethod
    def _generate_default_args(metadata: ComponentMetadata) -> str:
        """Generate default args for interaction/a11y tests"""
        args = []

        # Add children if needed
        if metadata.has_children:
            args.append(f"    children: '{metadata.name}',")

        # Add onClick for buttons
        if metadata.component_type == "button":
            if any(p.name == "onClick" for p in metadata.props):
                args.append("    onClick: () => {},")

        return "\n".join(args)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Storybook stories from component"
    )
    parser.add_argument("component_path", help="Path to component file")
    parser.add_argument(
        "--level",
        "-l",
        choices=["full", "standard", "basic", "minimal"],
        default="full",
        help="Testing level (default: full)",
    )
    parser.add_argument(
        "--output", "-o", help="Output file path (default: ComponentName.stories.tsx)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print to stdout instead of writing file"
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        output_path = args.output
    elif args.dry_run:
        output_path = None
    else:
        component_path = Path(args.component_path)
        output_path = (
            component_path.parent
            / f"{component_path.stem}.stories{component_path.suffix}"
        )

    # Generate story
    story_content = StoryGenerator.generate_story(
        args.component_path, args.level, output_path if not args.dry_run else None
    )

    # Print to stdout if dry run
    if args.dry_run and story_content:
        print(story_content)


if __name__ == "__main__":
    main()
