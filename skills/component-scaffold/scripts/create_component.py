#!/usr/bin/env python3
"""
Component Scaffold Generator

Generates framework-specific components with TypeScript, accessibility,
and best practices built-in.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"


@dataclass
class PropDefinition:
    """Component prop definition"""

    name: str
    type: str
    required: bool
    default: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ComponentSpec:
    """Component specification"""

    name: str
    component_type: str
    framework: str
    typescript: bool
    props: List[PropDefinition]
    has_children: bool
    description: str


# Component type definitions with default props
COMPONENT_TYPE_DEFAULTS = {
    "button": {
        "description": "Interactive button component with multiple variants and sizes",
        "props": [
            PropDefinition(
                "variant",
                "'primary' | 'secondary' | 'outline' | 'ghost'",
                False,
                "'primary'",
                "Visual style variant",
            ),
            PropDefinition(
                "size", "'small' | 'medium' | 'large'", False, "'medium'", "Button size"
            ),
            PropDefinition("disabled", "boolean", False, "false", "Disabled state"),
            PropDefinition("loading", "boolean", False, "false", "Loading state"),
            PropDefinition("onClick", "() => void", False, None, "Click handler"),
        ],
        "has_children": True,
    },
    "input": {
        "description": "Form input component with validation and error states",
        "props": [
            PropDefinition("label", "string", True, None, "Input label"),
            PropDefinition(
                "type",
                "'text' | 'email' | 'password' | 'number'",
                False,
                "'text'",
                "Input type",
            ),
            PropDefinition("placeholder", "string", False, None, "Placeholder text"),
            PropDefinition("value", "string", False, None, "Input value"),
            PropDefinition("error", "string", False, None, "Error message"),
            PropDefinition("helperText", "string", False, None, "Helper text"),
            PropDefinition("required", "boolean", False, "false", "Required field"),
            PropDefinition("disabled", "boolean", False, "false", "Disabled state"),
            PropDefinition(
                "onChange", "(value: string) => void", False, None, "Change handler"
            ),
        ],
        "has_children": False,
    },
    "card": {
        "description": "Card component for content containers",
        "props": [
            PropDefinition(
                "variant",
                "'elevated' | 'outlined' | 'flat'",
                False,
                "'elevated'",
                "Card style variant",
            ),
            PropDefinition("image", "string", False, None, "Card image URL"),
            PropDefinition("imageAlt", "string", False, None, "Image alt text"),
            PropDefinition(
                "header", "React.ReactNode", False, None, "Card header content"
            ),
            PropDefinition(
                "footer", "React.ReactNode", False, None, "Card footer content"
            ),
            PropDefinition("onClick", "() => void", False, None, "Click handler"),
        ],
        "has_children": True,
    },
    "modal": {
        "description": "Modal dialog component with focus management",
        "props": [
            PropDefinition("isOpen", "boolean", True, None, "Open state"),
            PropDefinition("onClose", "() => void", True, None, "Close handler"),
            PropDefinition("title", "string", False, None, "Modal title"),
            PropDefinition(
                "size",
                "'small' | 'medium' | 'large' | 'fullscreen'",
                False,
                "'medium'",
                "Modal size",
            ),
            PropDefinition(
                "closeOnBackdropClick",
                "boolean",
                False,
                "true",
                "Close on backdrop click",
            ),
            PropDefinition("closeOnEsc", "boolean", False, "true", "Close on ESC key"),
        ],
        "has_children": True,
    },
    "table": {
        "description": "Data table component with sorting and pagination",
        "props": [
            PropDefinition("data", "T[]", True, None, "Table data"),
            PropDefinition(
                "columns", "TableColumn<T>[]", True, None, "Column definitions"
            ),
            PropDefinition("sortable", "boolean", False, "false", "Enable sorting"),
            PropDefinition(
                "selectable", "boolean", False, "false", "Enable row selection"
            ),
            PropDefinition(
                "pagination", "boolean", False, "false", "Enable pagination"
            ),
            PropDefinition("pageSize", "number", False, "10", "Rows per page"),
            PropDefinition("loading", "boolean", False, "false", "Loading state"),
            PropDefinition(
                "emptyMessage", "string", False, "'No data'", "Empty state message"
            ),
            PropDefinition(
                "onRowClick", "(row: T) => void", False, None, "Row click handler"
            ),
        ],
        "has_children": False,
    },
    "custom": {
        "description": "Custom component",
        "props": [],
        "has_children": True,
    },
}


class ComponentGenerator:
    """Generates component files from templates"""

    @staticmethod
    def parse_custom_props(props_str: str) -> List[PropDefinition]:
        """Parse custom props from string format: 'name:type,name2:type2'"""
        props = []

        if not props_str:
            return props

        for prop_def in props_str.split(","):
            prop_def = prop_def.strip()
            if ":" not in prop_def:
                print(
                    f"Warning: Invalid prop format '{prop_def}', expected 'name:type'",
                    file=sys.stderr,
                )
                continue

            name, type_str = prop_def.split(":", 1)
            name = name.strip()
            type_str = type_str.strip()

            # Map common type shortcuts
            type_map = {
                "string": "string",
                "str": "string",
                "number": "number",
                "num": "number",
                "boolean": "boolean",
                "bool": "boolean",
                "function": "() => void",
                "func": "() => void",
                "node": "React.ReactNode",
                "element": "React.ReactNode",
            }

            typescript_type = type_map.get(type_str.lower(), type_str)

            props.append(
                PropDefinition(
                    name=name, type=typescript_type, required=False, default=None
                )
            )

        return props

    @staticmethod
    def get_component_spec(
        name: str,
        component_type: str,
        framework: str,
        typescript: bool,
        custom_props: Optional[str] = None,
    ) -> ComponentSpec:
        """Build component specification"""

        if component_type not in COMPONENT_TYPE_DEFAULTS:
            raise ValueError(f"Unknown component type: {component_type}")

        defaults = COMPONENT_TYPE_DEFAULTS[component_type]

        # For custom type, parse custom props
        if component_type == "custom" and custom_props:
            props = ComponentGenerator.parse_custom_props(custom_props)
        else:
            props = defaults["props"].copy()

        # Add children prop if needed
        if defaults["has_children"]:
            children_type = {"react": "React.ReactNode", "vue": "any", "svelte": "any"}[
                framework
            ]

            props.append(
                PropDefinition(
                    name="children",
                    type=children_type,
                    required=True if component_type != "custom" else False,
                    description="Component children",
                )
            )

        return ComponentSpec(
            name=name,
            component_type=component_type,
            framework=framework,
            typescript=typescript,
            props=props,
            has_children=defaults["has_children"],
            description=defaults["description"],
        )

    @staticmethod
    def to_kebab_case(name: str) -> str:
        """Convert PascalCase to kebab-case"""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1).lower()

    @staticmethod
    def load_template(framework: str, component_type: str) -> str:
        """Load component template"""
        template_file = TEMPLATES_DIR / framework / f"{component_type}.template"

        # Fallback to custom template if specific type not found
        if not template_file.exists():
            template_file = TEMPLATES_DIR / framework / "custom.template"

        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")

        with open(template_file, "r") as f:
            return f.read()

    @staticmethod
    def generate_props_interface(spec: ComponentSpec) -> str:
        """Generate TypeScript props interface"""
        lines = []

        for prop in spec.props:
            # Add JSDoc comment if description available
            if prop.description:
                lines.append(f"  /** {prop.description} */")

            # Build prop line
            optional = "?" if not prop.required else ""
            lines.append(f"  {prop.name}{optional}: {prop.type};")

        return "\n".join(lines)

    @staticmethod
    def generate_prop_destructuring(spec: ComponentSpec) -> str:
        """Generate prop destructuring with defaults"""
        parts = []

        for prop in spec.props:
            if prop.default:
                parts.append(f"{prop.name} = {prop.default}")
            else:
                parts.append(prop.name)

        # Format nicely if many props
        if len(parts) > 3:
            return ",\n  ".join(parts)
        else:
            return ", ".join(parts)

    @staticmethod
    def generate_component_content_react(spec: ComponentSpec) -> str:
        """Generate React component content based on type"""

        if spec.component_type == "button":
            return """<button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
    >
      {loading ? 'Loading...' : children}
    </button>"""

        elif spec.component_type == "input":
            return """<div className="input-wrapper">
      <label htmlFor={id} className="input-label">
        {label}
        {required && <span className="required">*</span>}
      </label>
      <input
        id={id}
        type={type}
        className={`input ${error ? 'input-error' : ''}`}
        placeholder={placeholder}
        value={value}
        disabled={disabled}
        required={required}
        onChange={(e) => onChange?.(e.target.value)}
        aria-invalid={!!error}
        aria-describedby={error ? `${id}-error` : helperText ? `${id}-helper` : undefined}
      />
      {error && <div id={`${id}-error`} className="input-error-message">{error}</div>}
      {helperText && !error && <div id={`${id}-helper`} className="input-helper">{helperText}</div>}
    </div>"""

        elif spec.component_type == "card":
            return """<div className={`card card-${variant}`} onClick={onClick}>
      {image && <img src={image} alt={imageAlt || ''} className="card-image" />}
      {header && <div className="card-header">{header}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>"""

        elif spec.component_type == "modal":
            return """<>
      {isOpen && (
        <div className="modal-overlay" onClick={closeOnBackdropClick ? onClose : undefined}>
          <div
            className={`modal modal-${size}`}
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'modal-title' : undefined}
          >
            {title && <h2 id="modal-title" className="modal-title">{title}</h2>}
            <button className="modal-close" onClick={onClose} aria-label="Close">
              ×
            </button>
            <div className="modal-content">{children}</div>
          </div>
        </div>
      )}
    </>"""

        else:
            # Generic content
            class_name = ComponentGenerator.to_kebab_case(spec.name)
            if spec.has_children:
                return f'<div className="{class_name}">\n      {{children}}\n    </div>'
            else:
                comment = "{/* Component content */}"
                return f'<div className="{class_name}">\n      {comment}\n    </div>'

    @staticmethod
    def generate_component_logic_react(spec: ComponentSpec) -> str:
        """Generate React component logic (hooks, etc.)"""
        logic_parts = []

        # Add ID generation for input
        if spec.component_type == "input":
            logic_parts.append("const id = React.useId();")

        # Add ESC key handler for modal
        if spec.component_type == "modal":
            logic_parts.append("""React.useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEsc && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose, closeOnEsc]);""")

        return "\n\n  ".join(logic_parts) if logic_parts else ""

    @staticmethod
    def generate_component(
        spec: ComponentSpec, output_path: Optional[str] = None
    ) -> str:
        """Generate complete component file"""

        # Load template
        template = ComponentGenerator.load_template(spec.framework, spec.component_type)

        # Generate parts
        props_interface = ComponentGenerator.generate_props_interface(spec)
        prop_destructuring = ComponentGenerator.generate_prop_destructuring(spec)

        if spec.framework == "react":
            component_content = ComponentGenerator.generate_component_content_react(
                spec
            )
            component_logic = ComponentGenerator.generate_component_logic_react(spec)
        else:
            component_content = f"<!-- {spec.name} component content -->"
            component_logic = ""

        # Replace template variables
        replacements = {
            "{{COMPONENT_NAME}}": spec.name,
            "{{COMPONENT_CLASS}}": ComponentGenerator.to_kebab_case(spec.name),
            "{{COMPONENT_DESCRIPTION}}": spec.description,
            "{{PROPS}}": props_interface,
            "{{PROP_DESTRUCTURING}}": prop_destructuring,
            "{{COMPONENT_LOGIC}}": component_logic,
            "{{COMPONENT_CONTENT}}": component_content,
        }

        component_code = template
        for placeholder, value in replacements.items():
            component_code = component_code.replace(placeholder, value)

        # Write to file if output path provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                f.write(component_code)

            print(f"✅ Component generated: {output_path}")

        return component_code


def main():
    parser = argparse.ArgumentParser(
        description="Generate framework-specific components with TypeScript and best practices"
    )
    parser.add_argument("--name", required=True, help="Component name (PascalCase)")
    parser.add_argument(
        "--type",
        choices=["button", "input", "card", "modal", "table", "custom"],
        default="custom",
        help="Component type",
    )
    parser.add_argument(
        "--framework",
        choices=["react", "vue", "svelte"],
        default="react",
        help="Target framework",
    )
    parser.add_argument(
        "--typescript", action="store_true", default=True, help="Generate TypeScript"
    )
    parser.add_argument(
        "--props", help="Custom props (comma-separated: name:type,name2:type2)"
    )
    parser.add_argument("--output", help="Output file path")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print to stdout instead of file"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output component spec as JSON"
    )

    args = parser.parse_args()

    try:
        # Validate component name
        if not args.name[0].isupper():
            print(
                "❌ Component name must start with uppercase letter (PascalCase)",
                file=sys.stderr,
            )
            sys.exit(1)

        # Build component spec
        spec = ComponentGenerator.get_component_spec(
            name=args.name,
            component_type=args.type,
            framework=args.framework,
            typescript=args.typescript,
            custom_props=args.props,
        )

        if args.json:
            # Output spec as JSON
            spec_dict = {
                "name": spec.name,
                "type": spec.component_type,
                "framework": spec.framework,
                "typescript": spec.typescript,
                "description": spec.description,
                "props": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "required": p.required,
                        "default": p.default,
                        "description": p.description,
                    }
                    for p in spec.props
                ],
                "has_children": spec.has_children,
            }
            print(json.dumps(spec_dict, indent=2))
        else:
            # Generate component
            if args.dry_run:
                component_code = ComponentGenerator.generate_component(spec)
                print(component_code)
            else:
                if not args.output:
                    print("❌ --output is required (or use --dry-run)", file=sys.stderr)
                    sys.exit(1)

                ComponentGenerator.generate_component(spec, args.output)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
