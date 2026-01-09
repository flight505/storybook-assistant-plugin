#!/usr/bin/env python3
"""
Component parser for React/TypeScript, Vue, and Svelte
Extracts component metadata: name, props, types, variants
"""

import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class PropDefinition:
    name: str
    type: str
    required: bool
    default_value: Optional[str] = None
    description: Optional[str] = None

@dataclass
class ComponentMetadata:
    name: str
    file_path: str
    framework: str  # 'react', 'vue', 'svelte'
    props: List[PropDefinition]
    component_type: str  # 'button', 'input', 'card', 'table', etc.
    has_children: bool
    exports_default: bool

class ComponentParser:
    """Base parser class"""

    @staticmethod
    def classify_component(name: str, props: List[PropDefinition]) -> str:
        """Classify component type based on name and props"""
        name_lower = name.lower()

        # Form inputs
        if any(term in name_lower for term in ['button', 'btn']):
            return 'button'
        if any(term in name_lower for term in ['input', 'textfield', 'textarea']):
            return 'input'
        if any(term in name_lower for term in ['select', 'dropdown', 'combo']):
            return 'select'
        if any(term in name_lower for term in ['checkbox', 'check']):
            return 'checkbox'
        if any(term in name_lower for term in ['radio']):
            return 'radio'
        if any(term in name_lower for term in ['switch', 'toggle']):
            return 'switch'

        # Layout
        if any(term in name_lower for term in ['card']):
            return 'card'
        if any(term in name_lower for term in ['modal', 'dialog']):
            return 'modal'
        if any(term in name_lower for term in ['sidebar', 'drawer']):
            return 'sidebar'
        if any(term in name_lower for term in ['container', 'box', 'grid']):
            return 'layout'

        # Data display
        if any(term in name_lower for term in ['table', 'datagrid']):
            return 'table'
        if any(term in name_lower for term in ['list']):
            return 'list'
        if any(term in name_lower for term in ['chart', 'graph']):
            return 'chart'
        if any(term in name_lower for term in ['badge', 'tag', 'chip']):
            return 'badge'
        if any(term in name_lower for term in ['avatar']):
            return 'avatar'

        # Feedback
        if any(term in name_lower for term in ['alert', 'notification']):
            return 'alert'
        if any(term in name_lower for term in ['toast', 'snackbar']):
            return 'toast'
        if any(term in name_lower for term in ['progress', 'loader', 'spinner']):
            return 'progress'

        # Navigation
        if any(term in name_lower for term in ['menu', 'nav']):
            return 'menu'
        if any(term in name_lower for term in ['tab']):
            return 'tabs'
        if any(term in name_lower for term in ['breadcrumb']):
            return 'breadcrumb'
        if any(term in name_lower for term in ['pagination', 'pager']):
            return 'pagination'

        return 'other'

class ReactTypeScriptParser(ComponentParser):
    """Parser for React/TypeScript components"""

    @staticmethod
    def parse(file_path: str) -> Optional[ComponentMetadata]:
        """Parse React TypeScript component"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract component name
            name = ReactTypeScriptParser._extract_component_name(content, file_path)
            if not name:
                return None

            # Extract props
            props = ReactTypeScriptParser._extract_props(content, name)

            # Check for children
            has_children = any(p.name == 'children' for p in props)

            # Check for default export
            exports_default = 'export default' in content

            # Classify component
            component_type = ComponentParser.classify_component(name, props)

            return ComponentMetadata(
                name=name,
                file_path=file_path,
                framework='react',
                props=props,
                component_type=component_type,
                has_children=has_children,
                exports_default=exports_default
            )

        except Exception as e:
            print(f"Error parsing {file_path}: {e}", file=sys.stderr)
            return None

    @staticmethod
    def _extract_component_name(content: str, file_path: str) -> Optional[str]:
        """Extract component name from file"""

        # Try function component: function ComponentName
        match = re.search(r'function\s+([A-Z][A-Za-z0-9_]*)', content)
        if match:
            return match.group(1)

        # Try arrow function: const ComponentName =
        match = re.search(r'const\s+([A-Z][A-Za-z0-9_]*)\s*[=:]', content)
        if match:
            return match.group(1)

        # Try export: export function ComponentName
        match = re.search(r'export\s+(?:default\s+)?function\s+([A-Z][A-Za-z0-9_]*)', content)
        if match:
            return match.group(1)

        # Fallback: use filename
        return Path(file_path).stem

    @staticmethod
    def _extract_props(content: str, component_name: str) -> List[PropDefinition]:
        """Extract props from TypeScript interface or type"""
        props = []

        # Find interface or type definition
        # Pattern: interface ButtonProps { ... }
        interface_pattern = rf'interface\s+{component_name}Props\s*\{{([^}}]+)\}}'
        match = re.search(interface_pattern, content, re.DOTALL)

        if not match:
            # Try generic Props interface
            interface_pattern = r'interface\s+Props\s*\{([^}]+)\}'
            match = re.search(interface_pattern, content, re.DOTALL)

        if not match:
            # Try type definition
            type_pattern = rf'type\s+{component_name}Props\s*=\s*\{{([^}}]+)\}}'
            match = re.search(type_pattern, content, re.DOTALL)

        if not match:
            # Try generic Props type
            type_pattern = r'type\s+Props\s*=\s*\{([^}]+)\}'
            match = re.search(type_pattern, content, re.DOTALL)

        if match:
            props_block = match.group(1)

            # Parse each prop
            # Pattern: propName?: type; or propName: type;
            prop_pattern = r'(\w+)(\?)?:\s*([^;]+);?'

            for prop_match in re.finditer(prop_pattern, props_block):
                name = prop_match.group(1)
                optional = prop_match.group(2) == '?'
                prop_type = prop_match.group(3).strip()

                # Clean up type (remove newlines, extra spaces)
                prop_type = ' '.join(prop_type.split())

                props.append(PropDefinition(
                    name=name,
                    type=prop_type,
                    required=not optional
                ))

        return props

class VueParser(ComponentParser):
    """Parser for Vue 3 components"""

    @staticmethod
    def parse(file_path: str) -> Optional[ComponentMetadata]:
        """Parse Vue component"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract component name from filename
            name = Path(file_path).stem

            # Extract props from defineProps
            props = VueParser._extract_props(content)

            # Check for slots (Vue's version of children)
            has_children = '<slot' in content

            # Classify component
            component_type = ComponentParser.classify_component(name, props)

            return ComponentMetadata(
                name=name,
                file_path=file_path,
                framework='vue',
                props=props,
                component_type=component_type,
                has_children=has_children,
                exports_default=True
            )

        except Exception as e:
            print(f"Error parsing {file_path}: {e}", file=sys.stderr)
            return None

    @staticmethod
    def _extract_props(content: str) -> List[PropDefinition]:
        """Extract props from defineProps"""
        props = []

        # Pattern: defineProps<{ ... }>()
        match = re.search(r'defineProps<\{([^}]+)\}>', content, re.DOTALL)

        if match:
            props_block = match.group(1)

            # Parse each prop
            prop_pattern = r'(\w+)(\?)?:\s*([^;,]+)'

            for prop_match in re.finditer(prop_pattern, props_block):
                name = prop_match.group(1)
                optional = prop_match.group(2) == '?'
                prop_type = prop_match.group(3).strip()

                props.append(PropDefinition(
                    name=name,
                    type=prop_type,
                    required=not optional
                ))

        # Also try runtime defineProps
        # Pattern: defineProps({ prop: { type: String, required: true } })
        runtime_match = re.search(r'defineProps\(\{([^}]+)\}\)', content, re.DOTALL)
        if runtime_match and not props:
            props_block = runtime_match.group(1)

            # Simple parsing for runtime props
            prop_pattern = r'(\w+):\s*\{[^}]*type:\s*(\w+)[^}]*required:\s*(true|false)?[^}]*\}'

            for prop_match in re.finditer(prop_pattern, props_block):
                name = prop_match.group(1)
                prop_type = prop_match.group(2)
                required_str = prop_match.group(3)
                required = required_str == 'true' if required_str else False

                props.append(PropDefinition(
                    name=name,
                    type=prop_type,
                    required=required
                ))

        return props

class SvelteParser(ComponentParser):
    """Parser for Svelte components"""

    @staticmethod
    def parse(file_path: str) -> Optional[ComponentMetadata]:
        """Parse Svelte component"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract component name from filename
            name = Path(file_path).stem

            # Extract props from export let
            props = SvelteParser._extract_props(content)

            # Check for slot
            has_children = '<slot' in content

            # Classify component
            component_type = ComponentParser.classify_component(name, props)

            return ComponentMetadata(
                name=name,
                file_path=file_path,
                framework='svelte',
                props=props,
                component_type=component_type,
                has_children=has_children,
                exports_default=True
            )

        except Exception as e:
            print(f"Error parsing {file_path}: {e}", file=sys.stderr)
            return None

    @staticmethod
    def _extract_props(content: str) -> List[PropDefinition]:
        """Extract props from export let statements"""
        props = []

        # Pattern: export let propName: type = defaultValue;
        # or: export let propName: type;
        # or: export let propName = defaultValue;
        prop_pattern = r'export\s+let\s+(\w+)(?::\s*([^=;]+))?(?:\s*=\s*([^;]+))?;?'

        for match in re.finditer(prop_pattern, content):
            name = match.group(1)
            prop_type = match.group(2).strip() if match.group(2) else 'any'
            default = match.group(3).strip() if match.group(3) else None

            # If has default value, it's optional
            required = default is None

            props.append(PropDefinition(
                name=name,
                type=prop_type,
                required=required,
                default_value=default
            ))

        return props

def parse_component(file_path: str) -> Optional[ComponentMetadata]:
    """Parse component file and return metadata"""

    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()

    # Determine parser based on file extension
    if extension in ['.tsx', '.jsx', '.ts', '.js']:
        return ReactTypeScriptParser.parse(file_path)
    elif extension == '.vue':
        return VueParser.parse(file_path)
    elif extension == '.svelte':
        return SvelteParser.parse(file_path)
    else:
        print(f"Unsupported file type: {extension}", file=sys.stderr)
        return None

def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Parse component and extract metadata'
    )
    parser.add_argument(
        'file_path',
        help='Path to component file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )

    args = parser.parse_args()

    metadata = parse_component(args.file_path)

    if metadata:
        if args.json:
            # Convert to dict for JSON serialization
            data = asdict(metadata)
            print(json.dumps(data, indent=2))
        else:
            print(f"Component: {metadata.name}")
            print(f"Framework: {metadata.framework}")
            print(f"Type: {metadata.component_type}")
            print(f"Props ({len(metadata.props)}):")
            for prop in metadata.props:
                required_str = "required" if prop.required else "optional"
                default_str = f" = {prop.default_value}" if prop.default_value else ""
                print(f"  - {prop.name}: {prop.type} ({required_str}){default_str}")
    else:
        print("Failed to parse component", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
