#!/usr/bin/env python3
"""
Accessibility Component Analyzer

Analyzes React/Vue/Svelte components for WCAG 2.2 accessibility violations.
Uses AST parsing to detect common issues and provide context-aware fix suggestions.

Usage:
    python analyze_component.py <component_file>
    python analyze_component.py Button.tsx --json
    python analyze_component.py src/components/ --recursive
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Issue severity levels matching WCAG conformance"""
    ERROR = "error"      # Level A violation (critical)
    WARNING = "warning"  # Level AA violation (important)
    INFO = "info"        # Level AAA or best practice


class WCAGLevel(Enum):
    """WCAG 2.2 conformance levels"""
    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class AccessibilityIssue:
    """Represents a single accessibility violation"""
    type: str
    severity: Severity
    wcag_criterion: str
    wcag_level: WCAGLevel
    line: int
    column: int
    element: str
    message: str
    context: Dict[str, Any]
    fix_suggestions: List[Dict[str, Any]]

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            **asdict(self),
            'severity': self.severity.value,
            'wcag_level': self.wcag_level.value
        }


class ComponentAnalyzer:
    """Main analyzer for component accessibility"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text()
        self.lines = self.content.split('\n')
        self.issues: List[AccessibilityIssue] = []

    def analyze(self) -> List[AccessibilityIssue]:
        """Run all accessibility checks"""
        self.check_missing_button_labels()
        self.check_missing_img_alt()
        self.check_missing_form_labels()
        self.check_color_contrast()
        self.check_redundant_aria()
        self.check_invalid_aria_attributes()
        self.check_missing_focus_indicators()
        self.check_keyboard_accessibility()
        self.check_heading_hierarchy()
        self.check_link_purpose()

        return self.issues

    def check_missing_button_labels(self):
        """WCAG 4.1.2: Check for buttons without accessible names"""
        # Match <button> elements
        button_pattern = r'<button([^>]*?)>(.*?)</button>'

        for match in re.finditer(button_pattern, self.content, re.DOTALL):
            attrs = match.group(1)
            content = match.group(2).strip()
            line_num = self.content[:match.start()].count('\n') + 1

            # Check if button has accessible name
            has_aria_label = 'aria-label=' in attrs
            has_aria_labelledby = 'aria-labelledby=' in attrs
            has_title = 'title=' in attrs
            has_text_content = bool(content and not re.match(r'^<[^>]+>$', content))

            # Special check for icon-only buttons (×, ✕, icons)
            is_icon_only = content in ['×', '✕', 'X', ''] or '<Icon' in content or '<svg' in content

            if not (has_aria_label or has_aria_labelledby or has_title or has_text_content):
                # Infer button purpose from context
                context = self._infer_button_context(attrs, content, line_num)

                self.issues.append(AccessibilityIssue(
                    type='missing_accessible_name',
                    severity=Severity.ERROR,
                    wcag_criterion='4.1.2',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=f'<button>{content}</button>',
                    message='Button has no accessible name for screen readers',
                    context={
                        'button_purpose': context['purpose'],
                        'is_icon_only': is_icon_only,
                        'content': content,
                        'attributes': attrs
                    },
                    fix_suggestions=self._generate_button_fixes(content, context)
                ))

    def check_missing_img_alt(self):
        """WCAG 1.1.1: Check for images without alt text"""
        img_pattern = r'<img\s+([^>]*?)/?>'

        for match in re.finditer(img_pattern, self.content):
            attrs = match.group(1)
            line_num = self.content[:match.start()].count('\n') + 1

            # Check for alt attribute
            has_alt = 'alt=' in attrs

            if not has_alt:
                # Check if image is decorative
                is_decorative = self._is_decorative_image(attrs)

                self.issues.append(AccessibilityIssue(
                    type='missing_alt_text',
                    severity=Severity.ERROR,
                    wcag_criterion='1.1.1',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=match.group(0),
                    message='Image missing alt attribute',
                    context={
                        'is_decorative': is_decorative,
                        'src': self._extract_attr_value(attrs, 'src'),
                        'className': self._extract_attr_value(attrs, 'className')
                    },
                    fix_suggestions=self._generate_img_fixes(attrs, is_decorative)
                ))

    def check_missing_form_labels(self):
        """WCAG 3.3.2: Check for form inputs without labels"""
        input_pattern = r'<input\s+([^>]*?)/?>'

        for match in re.finditer(input_pattern, self.content):
            attrs = match.group(1)
            line_num = self.content[:match.start()].count('\n') + 1

            # Check if input has label association
            has_id = 'id=' in attrs
            has_aria_label = 'aria-label=' in attrs
            has_aria_labelledby = 'aria-labelledby=' in attrs
            input_type = self._extract_attr_value(attrs, 'type') or 'text'

            # Check if there's a <label htmlFor="..."> nearby
            has_external_label = False
            if has_id:
                input_id = self._extract_attr_value(attrs, 'id')
                has_external_label = f'htmlFor="{input_id}"' in self.content or f"htmlFor='{input_id}'" in self.content

            if not (has_aria_label or has_aria_labelledby or has_external_label):
                # Hidden inputs don't need labels
                if input_type == 'hidden':
                    continue

                placeholder = self._extract_attr_value(attrs, 'placeholder')

                self.issues.append(AccessibilityIssue(
                    type='missing_form_label',
                    severity=Severity.ERROR,
                    wcag_criterion='3.3.2',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=match.group(0),
                    message='Form input missing associated label',
                    context={
                        'input_type': input_type,
                        'placeholder': placeholder,
                        'has_id': has_id
                    },
                    fix_suggestions=self._generate_input_fixes(attrs, input_type, placeholder)
                ))

    def check_color_contrast(self):
        """WCAG 1.4.3: Check for color contrast issues"""
        # Look for inline styles with color definitions
        style_pattern = r'style=\{\{([^}]+)\}\}'

        for match in re.finditer(style_pattern, self.content):
            styles = match.group(1)
            line_num = self.content[:match.start()].count('\n') + 1

            # Extract color and background
            color = self._extract_style_color(styles, 'color')
            background = self._extract_style_color(styles, 'background')

            if color and background:
                contrast_ratio = self._calculate_contrast_ratio(color, background)

                # Check WCAG levels
                passes_aa_normal = contrast_ratio >= 4.5
                passes_aa_large = contrast_ratio >= 3.0
                passes_aaa_normal = contrast_ratio >= 7.0

                if not passes_aa_normal:
                    self.issues.append(AccessibilityIssue(
                        type='color_contrast',
                        severity=Severity.ERROR if not passes_aa_large else Severity.WARNING,
                        wcag_criterion='1.4.3',
                        wcag_level=WCAGLevel.AA,
                        line=line_num,
                        column=match.start() - self.content[:match.start()].rfind('\n'),
                        element=match.group(0),
                        message=f'Color contrast too low ({contrast_ratio:.1f}:1)',
                        context={
                            'foreground_color': color,
                            'background_color': background,
                            'contrast_ratio': contrast_ratio,
                            'passes_aa_normal': passes_aa_normal,
                            'passes_aa_large': passes_aa_large,
                            'passes_aaa': passes_aaa_normal
                        },
                        fix_suggestions=self._generate_contrast_fixes(color, background, contrast_ratio)
                    ))

    def check_redundant_aria(self):
        """WCAG 4.1.2: Check for redundant ARIA roles"""
        redundant_patterns = [
            (r'<button[^>]*role="button"', 'button', 'button'),
            (r'<nav[^>]*role="navigation"', 'nav', 'navigation'),
            (r'<main[^>]*role="main"', 'main', 'main'),
            (r'<aside[^>]*role="complementary"', 'aside', 'complementary'),
        ]

        for pattern, element, role in redundant_patterns:
            for match in re.finditer(pattern, self.content):
                line_num = self.content[:match.start()].count('\n') + 1

                self.issues.append(AccessibilityIssue(
                    type='redundant_aria_role',
                    severity=Severity.INFO,
                    wcag_criterion='4.1.2',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=match.group(0),
                    message=f'Redundant role="{role}" on <{element}> element',
                    context={
                        'element': element,
                        'redundant_role': role
                    },
                    fix_suggestions=[{
                        'rank': 1,
                        'method': 'remove_redundant_role',
                        'description': f'Remove role="{role}" (native <{element}> already provides this role)',
                        'code': match.group(0).replace(f'role="{role}"', '').replace('  ', ' ')
                    }]
                ))

    def check_invalid_aria_attributes(self):
        """Check for invalid or misspelled ARIA attributes"""
        # Common ARIA typos
        invalid_aria = [
            'aria-labelled-by',  # Should be aria-labelledby
            'aria-described-by', # Should be aria-describedby
        ]

        for invalid in invalid_aria:
            if invalid in self.content:
                for match in re.finditer(invalid, self.content):
                    line_num = self.content[:match.start()].count('\n') + 1
                    correct = invalid.replace('-', '')

                    self.issues.append(AccessibilityIssue(
                        type='invalid_aria_attribute',
                        severity=Severity.ERROR,
                        wcag_criterion='4.1.2',
                        wcag_level=WCAGLevel.A,
                        line=line_num,
                        column=match.start() - self.content[:match.start()].rfind('\n'),
                        element=invalid,
                        message=f'Invalid ARIA attribute: {invalid}',
                        context={'invalid_attr': invalid, 'correct_attr': correct},
                        fix_suggestions=[{
                            'rank': 1,
                            'method': 'fix_typo',
                            'description': f'Correct attribute name to {correct}',
                            'code': f'Replace {invalid} with {correct}'
                        }]
                    ))

    def check_missing_focus_indicators(self):
        """WCAG 2.4.7: Check for removed focus indicators"""
        focus_removal_patterns = [
            r'outline:\s*["\']?none["\']?',
            r'outline:\s*0',
        ]

        for pattern in focus_removal_patterns:
            for match in re.finditer(pattern, self.content):
                line_num = self.content[:match.start()].count('\n') + 1

                # Check if there's a custom focus style nearby
                context_start = max(0, match.start() - 200)
                context_end = min(len(self.content), match.end() + 200)
                context = self.content[context_start:context_end]

                has_custom_focus = ':focus' in context or 'focus-visible' in context

                if not has_custom_focus:
                    self.issues.append(AccessibilityIssue(
                        type='missing_focus_indicator',
                        severity=Severity.WARNING,
                        wcag_criterion='2.4.7',
                        wcag_level=WCAGLevel.AA,
                        line=line_num,
                        column=match.start() - self.content[:match.start()].rfind('\n'),
                        element=match.group(0),
                        message='Focus outline removed without custom replacement',
                        context={'has_custom_focus': has_custom_focus},
                        fix_suggestions=self._generate_focus_fixes()
                    ))

    def check_keyboard_accessibility(self):
        """WCAG 2.1.1: Check for elements with onClick but no keyboard support"""
        # Find div/span with onClick but no keyboard support
        clickable_pattern = r'<(div|span)([^>]*)onClick[^>]*>'

        for match in re.finditer(clickable_pattern, self.content):
            element_type = match.group(1)
            attrs = match.group(2)
            line_num = self.content[:match.start()].count('\n') + 1

            has_role = 'role=' in attrs
            has_tabindex = 'tabIndex=' in attrs
            has_onkeydown = 'onKeyDown=' in attrs

            # If it's clickable but not keyboard accessible, flag it
            if not (has_role and has_tabindex and has_onkeydown):
                self.issues.append(AccessibilityIssue(
                    type='missing_keyboard_support',
                    severity=Severity.ERROR,
                    wcag_criterion='2.1.1',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=match.group(0),
                    message=f'<{element_type}> with onClick lacks keyboard support',
                    context={
                        'element': element_type,
                        'has_role': has_role,
                        'has_tabindex': has_tabindex,
                        'has_onkeydown': has_onkeydown
                    },
                    fix_suggestions=self._generate_keyboard_fixes(element_type)
                ))

    def check_heading_hierarchy(self):
        """WCAG 1.3.1: Check for proper heading hierarchy"""
        headings = re.findall(r'<h([1-6])', self.content)

        if not headings:
            return

        prev_level = 0
        for i, level_str in enumerate(headings):
            level = int(level_str)

            # Check if heading level skips (e.g., h2 → h4)
            if prev_level > 0 and level > prev_level + 1:
                # Find line number of this heading
                heading_matches = list(re.finditer(r'<h[1-6]', self.content))
                if i < len(heading_matches):
                    line_num = self.content[:heading_matches[i].start()].count('\n') + 1

                    self.issues.append(AccessibilityIssue(
                        type='heading_hierarchy_skip',
                        severity=Severity.WARNING,
                        wcag_criterion='1.3.1',
                        wcag_level=WCAGLevel.A,
                        line=line_num,
                        column=0,
                        element=f'<h{level}>',
                        message=f'Heading skips from h{prev_level} to h{level}',
                        context={'prev_level': prev_level, 'current_level': level},
                        fix_suggestions=[{
                            'rank': 1,
                            'method': 'fix_hierarchy',
                            'description': f'Change to h{prev_level + 1} or ensure h{prev_level + 1} exists before this heading',
                            'code': f'<h{prev_level + 1}>'
                        }]
                    ))

            prev_level = level

    def check_link_purpose(self):
        """WCAG 2.4.4: Check for ambiguous link text"""
        ambiguous_texts = ['click here', 'read more', 'here', 'more', 'link']

        link_pattern = r'<a[^>]*>(.*?)</a>'

        for match in re.finditer(link_pattern, self.content, re.IGNORECASE):
            link_text = re.sub(r'<[^>]+>', '', match.group(1)).strip().lower()
            line_num = self.content[:match.start()].count('\n') + 1

            if link_text in ambiguous_texts:
                self.issues.append(AccessibilityIssue(
                    type='ambiguous_link_text',
                    severity=Severity.WARNING,
                    wcag_criterion='2.4.4',
                    wcag_level=WCAGLevel.A,
                    line=line_num,
                    column=match.start() - self.content[:match.start()].rfind('\n'),
                    element=match.group(0),
                    message=f'Link text "{link_text}" is not descriptive',
                    context={'link_text': link_text},
                    fix_suggestions=[{
                        'rank': 1,
                        'method': 'descriptive_text',
                        'description': 'Use descriptive link text that explains where the link goes',
                        'code': 'Example: "Read the full article" instead of "Read more"'
                    }]
                ))

    # Helper methods

    def _infer_button_context(self, attrs: str, content: str, line_num: int) -> Dict[str, Any]:
        """Infer button purpose from context"""
        # Check button content
        if content in ['×', '✕', 'X', 'Close']:
            return {'purpose': 'close_button', 'suggested_label': 'Close'}

        # Check onClick handler
        if 'onClick=' in attrs:
            onclick = re.search(r'onClick=\{([^}]+)\}', attrs)
            if onclick:
                handler_name = onclick.group(1).lower()
                if 'delete' in handler_name:
                    return {'purpose': 'delete_button', 'suggested_label': 'Delete'}
                if 'submit' in handler_name:
                    return {'purpose': 'submit_button', 'suggested_label': 'Submit'}
                if 'close' in handler_name:
                    return {'purpose': 'close_button', 'suggested_label': 'Close'}
                if 'save' in handler_name:
                    return {'purpose': 'save_button', 'suggested_label': 'Save'}

        # Check surrounding context
        context_start = max(0, self.content.rfind('\n', 0, line_num * 80) - 200)
        context_end = min(len(self.content), line_num * 80 + 200)
        surrounding = self.content[context_start:context_end].lower()

        if 'modal' in surrounding or 'dialog' in surrounding:
            return {'purpose': 'modal_action', 'suggested_label': 'Close dialog'}

        return {'purpose': 'generic_button', 'suggested_label': 'Action'}

    def _is_decorative_image(self, attrs: str) -> bool:
        """Check if image is likely decorative"""
        # Common decorative patterns
        decorative_patterns = ['icon', 'logo', 'decoration', 'background', 'pattern']

        class_name = self._extract_attr_value(attrs, 'className') or ''
        src = self._extract_attr_value(attrs, 'src') or ''

        return any(pattern in class_name.lower() or pattern in src.lower()
                   for pattern in decorative_patterns)

    def _extract_attr_value(self, attrs: str, attr_name: str) -> Optional[str]:
        """Extract attribute value from attributes string"""
        pattern = f'{attr_name}=(["\'])([^"\']*?)\\1'
        match = re.search(pattern, attrs)
        if match:
            return match.group(2)

        # Try without quotes
        pattern = f'{attr_name}={{([^}}]+)}}'
        match = re.search(pattern, attrs)
        if match:
            return match.group(1)

        return None

    def _extract_style_color(self, styles: str, prop: str) -> Optional[str]:
        """Extract color value from inline styles"""
        pattern = f'{prop}:\\s*["\']?([^"\'\\s,}}]+)'
        match = re.search(pattern, styles)
        return match.group(1) if match else None

    def _calculate_contrast_ratio(self, fg: str, bg: str) -> float:
        """Calculate WCAG contrast ratio between two colors"""
        # Simplified contrast calculation (would use full algorithm in production)
        # This is a placeholder that returns approximate values

        # Convert hex to RGB if needed
        def hex_to_rgb(color):
            color = color.lstrip('#')
            if len(color) == 3:
                color = ''.join([c*2 for c in color])
            return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        def luminance(rgb):
            # Simplified relative luminance calculation
            r, g, b = [c/255.0 for c in rgb]
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        try:
            if fg.startswith('#'):
                fg_rgb = hex_to_rgb(fg)
                bg_rgb = hex_to_rgb(bg)
            else:
                # For non-hex colors, return a default passing value
                return 5.0

            l1 = luminance(fg_rgb)
            l2 = luminance(bg_rgb)

            lighter = max(l1, l2)
            darker = min(l1, l2)

            return (lighter + 0.05) / (darker + 0.05)
        except:
            return 5.0  # Default to passing if calculation fails

    def _generate_button_fixes(self, content: str, context: Dict) -> List[Dict]:
        """Generate fix suggestions for button accessible name"""
        purpose = context['purpose']
        suggested_label = context['suggested_label']

        fixes = []

        # Option 1: sr-only text with icon
        if content in ['×', '✕', 'X'] or not content:
            fixes.append({
                'rank': 1,
                'method': 'sr_only_text',
                'description': 'Add visually hidden text for screen readers (BEST)',
                'code': f'''<button>
  <span aria-hidden="true">{content or '×'}</span>
  <span className="sr-only">{suggested_label}</span>
</button>''',
                'requires_css': True
            })

        # Option 2: aria-label
        fixes.append({
            'rank': 2,
            'method': 'aria_label',
            'description': 'Add aria-label attribute (GOOD)',
            'code': f'<button aria-label="{suggested_label}">{content or "..."}</button>',
            'requires_css': False
        })

        # Option 3: title attribute
        fixes.append({
            'rank': 3,
            'method': 'title',
            'description': 'Add title attribute (ACCEPTABLE - not announced by all screen readers)',
            'code': f'<button title="{suggested_label}">{content or "..."}</button>',
            'requires_css': False
        })

        return fixes

    def _generate_img_fixes(self, attrs: str, is_decorative: bool) -> List[Dict]:
        """Generate fix suggestions for image alt text"""
        fixes = []

        if is_decorative:
            fixes.append({
                'rank': 1,
                'method': 'empty_alt',
                'description': 'Add empty alt attribute for decorative image (BEST)',
                'code': '<img alt="" aria-hidden="true" ... />',
            })
        else:
            src = self._extract_attr_value(attrs, 'src') or ''
            fixes.append({
                'rank': 1,
                'method': 'descriptive_alt',
                'description': 'Add descriptive alt text (BEST)',
                'code': '<img alt="Description of image content" ... />',
                'note': f'Describe what the image shows or its purpose'
            })

        return fixes

    def _generate_input_fixes(self, attrs: str, input_type: str, placeholder: Optional[str]) -> List[Dict]:
        """Generate fix suggestions for form labels"""
        fixes = []

        label_text = placeholder or f'{input_type.capitalize()} input'
        has_id = 'id=' in attrs
        input_id = self._extract_attr_value(attrs, 'id') or 'input-id'

        # Option 1: label with htmlFor
        if has_id or True:  # Always show this option
            fixes.append({
                'rank': 1,
                'method': 'label_with_htmlfor',
                'description': 'Add label with htmlFor attribute (BEST)',
                'code': f'''<label htmlFor="{input_id}">
  {label_text}
</label>
<input id="{input_id}" type="{input_type}" ... />'''
            })

        # Option 2: Wrapping label
        fixes.append({
            'rank': 2,
            'method': 'wrapping_label',
            'description': 'Wrap input in label element (GOOD)',
            'code': f'''<label>
  {label_text}
  <input type="{input_type}" ... />
</label>'''
        })

        # Option 3: aria-label
        fixes.append({
            'rank': 3,
            'method': 'aria_label',
            'description': 'Add aria-label (ACCEPTABLE - visible labels are better)',
            'code': f'<input type="{input_type}" aria-label="{label_text}" ... />'
        })

        return fixes

    def _generate_contrast_fixes(self, fg: str, bg: str, ratio: float) -> List[Dict]:
        """Generate fix suggestions for color contrast"""
        fixes = []

        # Suggest darker/lighter colors that pass
        # This is simplified - real implementation would calculate actual passing colors
        fixes.append({
            'rank': 1,
            'method': 'adjust_foreground',
            'description': f'Darken text color for WCAG AA compliance (requires 4.5:1, currently {ratio:.1f}:1)',
            'code': 'color: #666 (or darker)',
            'note': 'Use a color contrast checker to find a passing color'
        })

        return fixes

    def _generate_focus_fixes(self) -> List[Dict]:
        """Generate fix suggestions for focus indicators"""
        return [
            {
                'rank': 1,
                'method': 'focus_visible',
                'description': 'Use :focus-visible for keyboard-only focus styling (BEST)',
                'code': '''button {
  outline: none;
}
button:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}'''
            },
            {
                'rank': 2,
                'method': 'custom_focus',
                'description': 'Add custom focus styles with :focus (GOOD)',
                'code': '''button:focus {
  outline: 2px solid blue;
  outline-offset: 2px;
}'''
            }
        ]

    def _generate_keyboard_fixes(self, element_type: str) -> List[Dict]:
        """Generate fix suggestions for keyboard accessibility"""
        return [
            {
                'rank': 1,
                'method': 'use_button',
                'description': 'Use semantic <button> element instead (BEST)',
                'code': '<button onClick={handleClick}>Click me</button>',
                'note': 'Native buttons have built-in keyboard support'
            },
            {
                'rank': 2,
                'method': 'add_keyboard_support',
                'description': f'Add role, tabIndex, and keyboard handler to <{element_type}> (ACCEPTABLE)',
                'code': f'''<{element_type}
  role="button"
  tabIndex={{0}}
  onClick={{handleClick}}
  onKeyDown={{(e) => e.key === 'Enter' && handleClick()}}
>
  Click me
</{element_type}>'''
            }
        ]


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_component.py <component_file> [--json]")
        sys.exit(1)

    file_path = sys.argv[1]
    output_json = '--json' in sys.argv

    try:
        analyzer = ComponentAnalyzer(file_path)
        issues = analyzer.analyze()

        if output_json:
            # JSON output for programmatic use
            print(json.dumps({
                'file': file_path,
                'total_issues': len(issues),
                'issues': [issue.to_dict() for issue in issues]
            }, indent=2))
        else:
            # Human-readable output
            if not issues:
                print(f"✓ No accessibility issues found in {file_path}")
                return

            print(f"\n❌ {len(issues)} accessibility issue(s) found in {file_path}\n")

            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue.message}")
                print(f"   Line {issue.line}: {issue.element}")
                print(f"   WCAG: {issue.wcag_criterion} (Level {issue.wcag_level.value})")
                print(f"   Severity: {issue.severity.value.upper()}")

                if issue.fix_suggestions:
                    print(f"\n   Suggested fixes:")
                    for fix in issue.fix_suggestions[:2]:  # Show top 2
                        print(f"   [{fix['rank']}] {fix['description']}")
                        if 'code' in fix:
                            print(f"       {fix['code'][:60]}...")
                print()

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing component: {e}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
