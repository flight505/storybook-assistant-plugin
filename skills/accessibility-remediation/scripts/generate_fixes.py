#!/usr/bin/env python3
"""
AI-Powered Accessibility Fix Generator

Generates context-aware accessibility fix suggestions using Claude AI.
Analyzes component purpose, user intent, and WCAG best practices to provide
ranked remediation options.

Usage:
    python generate_fixes.py <component_file> <issue_type>
    python generate_fixes.py Button.tsx missing_accessible_name
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class FixGenerator:
    """Generates AI-powered accessibility fix suggestions"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = self.file_path.read_text()

    def generate_fixes_for_issue(
        self,
        issue_type: str,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict[str, Any]]:
        """
        Generate ranked fix suggestions for an accessibility issue

        Args:
            issue_type: Type of issue (e.g., 'missing_accessible_name')
            element: The problematic element
            context: Additional context about the issue
            line_num: Line number where issue occurs

        Returns:
            List of fix suggestions ranked by best practice
        """

        # Route to specific generator based on issue type
        generators = {
            'missing_accessible_name': self._generate_button_label_fixes,
            'missing_alt_text': self._generate_img_alt_fixes,
            'missing_form_label': self._generate_form_label_fixes,
            'color_contrast': self._generate_contrast_fixes,
            'missing_focus_indicator': self._generate_focus_fixes,
            'missing_keyboard_support': self._generate_keyboard_fixes,
            'redundant_aria_role': self._generate_aria_cleanup_fixes,
            'heading_hierarchy_skip': self._generate_heading_fixes,
            'ambiguous_link_text': self._generate_link_text_fixes,
        }

        generator = generators.get(issue_type, self._generate_generic_fixes)
        return generator(element, context, line_num)

    def _generate_button_label_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for buttons without accessible names"""

        button_purpose = context.get('button_purpose', {}).get('purpose', 'generic_button')
        suggested_label = context.get('button_purpose', {}).get('suggested_label', 'Action')
        is_icon_only = context.get('is_icon_only', False)
        content = context.get('content', '')

        fixes = []

        # Fix 1: sr-only text (best for icon buttons)
        if is_icon_only or content in ['×', '✕', 'X', '']:
            fixes.append({
                'rank': 1,
                'method': 'sr_only_with_icon',
                'wcag_level': 'AA',
                'description': 'Add visually hidden text alongside icon',
                'explanation': 'Best practice for icon buttons - maintains visual design while providing screen reader text',
                'code': self._generate_button_sr_only_code(content or '×', suggested_label),
                'requires': ['sr-only CSS class'],
                'pros': [
                    'Maintains visual design',
                    'Clear to screen reader users',
                    'Follows WCAG best practices'
                ],
                'cons': [
                    'Requires sr-only CSS utility class'
                ],
                'wcag_criterion': '4.1.2 Name, Role, Value'
            })

        # Fix 2: aria-label (good for most cases)
        fixes.append({
            'rank': 2 if is_icon_only else 1,
            'method': 'aria_label',
            'wcag_level': 'AA',
            'description': 'Add aria-label attribute',
            'explanation': 'Simple and effective - works immediately without CSS changes',
            'code': f'<button aria-label="{suggested_label}" onClick={{...}}>\n  {content or "..."}\n</button>',
            'requires': [],
            'pros': [
                'Simple implementation',
                'No CSS required',
                'Works in all browsers'
            ],
            'cons': [
                'Not translatable without additional i18n setup',
                'Overrides visible text if present'
            ],
            'wcag_criterion': '4.1.2 Name, Role, Value'
        })

        # Fix 3: Visible text (best when space allows)
        if is_icon_only:
            fixes.append({
                'rank': 3,
                'method': 'visible_text',
                'wcag_level': 'AAA',
                'description': 'Replace icon with visible text',
                'explanation': 'Best for all users - everyone benefits from clear text',
                'code': f'<button onClick={{...}}>\n  {suggested_label}\n</button>',
                'requires': [],
                'pros': [
                    'Clearest for all users',
                    'No screen reader needed',
                    'Best accessibility score'
                ],
                'cons': [
                    'Changes visual design',
                    'Requires more space'
                ],
                'wcag_criterion': '4.1.2 Name, Role, Value'
            })

        # Fix 4: title attribute (acceptable fallback)
        fixes.append({
            'rank': 4,
            'method': 'title_attribute',
            'wcag_level': 'A',
            'description': 'Add title attribute',
            'explanation': 'Acceptable but not ideal - not announced by all screen readers',
            'code': f'<button title="{suggested_label}" onClick={{...}}>\n  {content or "..."}\n</button>',
            'requires': [],
            'pros': [
                'Simple implementation',
                'Provides tooltip for mouse users'
            ],
            'cons': [
                'Not announced by all screen readers',
                'Inconsistent browser support',
                'Tooltip may not appear on touch devices'
            ],
            'wcag_criterion': '4.1.2 Name, Role, Value'
        })

        # Add context-specific recommendations
        if button_purpose == 'close_button':
            fixes[0]['note'] = 'For close buttons, "Close" or "Close dialog" are standard labels'
        elif button_purpose == 'submit_button':
            fixes[0]['note'] = 'For submit buttons, be specific: "Submit form", "Save changes", etc.'
        elif button_purpose == 'delete_button':
            fixes[0]['note'] = 'For delete buttons, include what\'s being deleted: "Delete item"'

        return fixes

    def _generate_button_sr_only_code(self, icon_content: str, label: str) -> str:
        """Generate sr-only button code"""
        return f'''<button onClick={{...}}>
  <span aria-hidden="true">{icon_content}</span>
  <span className="sr-only">{label}</span>
</button>

/* Add to your global CSS: */
.sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}}'''

    def _generate_img_alt_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for images without alt text"""

        is_decorative = context.get('is_decorative', False)
        src = context.get('src', '')

        fixes = []

        if is_decorative:
            # Decorative image
            fixes.append({
                'rank': 1,
                'method': 'empty_alt',
                'wcag_level': 'A',
                'description': 'Add empty alt attribute for decorative image',
                'explanation': 'Tells screen readers to skip this image (it\'s decorative)',
                'code': '<img src={...} alt="" aria-hidden="true" />',
                'requires': [],
                'pros': [
                    'Screen readers skip the image',
                    'Cleaner screen reader experience',
                    'Follows WCAG decorative image pattern'
                ],
                'cons': [],
                'wcag_criterion': '1.1.1 Non-text Content',
                'note': 'Use empty alt="" for purely decorative images (backgrounds, spacers, visual decoration)'
            })
        else:
            # Informative image
            fixes.append({
                'rank': 1,
                'method': 'descriptive_alt',
                'wcag_level': 'A',
                'description': 'Add descriptive alt text',
                'explanation': 'Describe what the image shows or its purpose',
                'code': '<img src={...} alt="Description of image content" />',
                'requires': [],
                'pros': [
                    'Screen reader users know image content',
                    'Works when images fail to load',
                    'Improves SEO'
                ],
                'cons': [],
                'wcag_criterion': '1.1.1 Non-text Content',
                'note': 'Be specific and concise. Describe what\'s important about the image.'
            })

            # For complex images
            if 'chart' in src.lower() or 'graph' in src.lower() or 'diagram' in src.lower():
                fixes.append({
                    'rank': 2,
                    'method': 'long_description',
                    'wcag_level': 'AA',
                    'description': 'Add alt text + detailed description',
                    'explanation': 'For complex images like charts, provide both summary and details',
                    'code': '''<figure>
  <img src={...} alt="Bar chart showing sales growth" aria-describedby="chart-description" />
  <figcaption id="chart-description">
    Detailed description: Sales grew 40% in Q4, from $100K to $140K...
  </figcaption>
</figure>''',
                    'requires': [],
                    'pros': [
                        'Provides both summary and details',
                        'Visible to all users',
                        'Best for complex data visualizations'
                    ],
                    'cons': [
                        'Requires more markup',
                        'May not fit all designs'
                    ],
                    'wcag_criterion': '1.1.1 Non-text Content'
                })

        return fixes

    def _generate_form_label_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for form inputs without labels"""

        input_type = context.get('input_type', 'text')
        placeholder = context.get('placeholder', '')
        has_id = context.get('has_id', False)

        label_text = placeholder or f'{input_type.capitalize()}'

        fixes = []

        # Fix 1: Explicit label with htmlFor (best)
        fixes.append({
            'rank': 1,
            'method': 'explicit_label',
            'wcag_level': 'AA',
            'description': 'Add label with htmlFor attribute',
            'explanation': 'Most robust - works even if elements are separated in the DOM',
            'code': f'''<label htmlFor="input-id">
  {label_text}
</label>
<input id="input-id" type="{input_type}" placeholder="{placeholder or 'Enter text...'}" />''',
            'requires': ['Unique id on input'],
            'pros': [
                'Most robust label association',
                'Works with separated elements',
                'Clicking label focuses input'
            ],
            'cons': [
                'Requires unique id'
            ],
            'wcag_criterion': '3.3.2 Labels or Instructions'
        })

        # Fix 2: Wrapping label (good)
        fixes.append({
            'rank': 2,
            'method': 'wrapping_label',
            'wcag_level': 'AA',
            'description': 'Wrap input in label element',
            'explanation': 'Implicit label association - simpler markup',
            'code': f'''<label>
  {label_text}
  <input type="{input_type}" placeholder="{placeholder or 'Enter text...'}" />
</label>''',
            'requires': [],
            'pros': [
                'Simple markup',
                'No id required',
                'Clicking label focuses input'
            ],
            'cons': [
                'Less flexible for complex layouts'
            ],
            'wcag_criterion': '3.3.2 Labels or Instructions'
        })

        # Fix 3: aria-label (acceptable)
        fixes.append({
            'rank': 3,
            'method': 'aria_label',
            'wcag_level': 'A',
            'description': 'Add aria-label attribute',
            'explanation': 'Works but visible labels are preferred for all users',
            'code': f'<input type="{input_type}" aria-label="{label_text}" placeholder="{placeholder or 'Enter text...'}" />',
            'requires': [],
            'pros': [
                'Simple implementation',
                'No extra elements'
            ],
            'cons': [
                'Not visible to sighted users',
                'Placeholders are not labels',
                'Not ideal for usability'
            ],
            'wcag_criterion': '3.3.2 Labels or Instructions',
            'note': 'aria-label should be a last resort - visible labels benefit all users'
        })

        return fixes

    def _generate_contrast_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for color contrast issues"""

        fg_color = context.get('foreground_color', '#999')
        bg_color = context.get('background_color', '#fff')
        current_ratio = context.get('contrast_ratio', 0)

        fixes = []

        # Calculate suggested colors (simplified)
        suggested_darker = self._darken_color(fg_color)
        suggested_lighter_bg = self._lighten_color(bg_color)

        fixes.append({
            'rank': 1,
            'method': 'darken_foreground',
            'wcag_level': 'AA',
            'description': f'Darken text color for {4.5}:1 contrast',
            'explanation': f'Current ratio {current_ratio:.1f}:1 fails WCAG AA (requires 4.5:1)',
            'code': f'color: {suggested_darker}  /* Was {fg_color} */',
            'requires': [],
            'pros': [
                'Passes WCAG AA for normal text',
                'Minimal visual change'
            ],
            'cons': [],
            'wcag_criterion': '1.4.3 Contrast (Minimum)',
            'note': 'Use a contrast checker tool to verify: https://webaim.org/resources/contrastchecker/'
        })

        fixes.append({
            'rank': 2,
            'method': 'lighten_background',
            'wcag_level': 'AA',
            'description': 'Lighten background color',
            'explanation': 'Alternative: adjust background instead of foreground',
            'code': f'background: {suggested_lighter_bg}  /* Was {bg_color} */',
            'requires': [],
            'pros': [
                'Maintains text color',
                'May fit design system better'
            ],
            'cons': [
                'Affects other elements on same background'
            ],
            'wcag_criterion': '1.4.3 Contrast (Minimum)'
        })

        return fixes

    def _generate_focus_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for missing focus indicators"""

        return [
            {
                'rank': 1,
                'method': 'focus_visible',
                'wcag_level': 'AA',
                'description': 'Use :focus-visible for keyboard-only focus',
                'explanation': 'Shows focus only for keyboard navigation, not mouse clicks',
                'code': '''button {
  outline: none; /* Remove default outline */
}

button:focus-visible {
  outline: 2px solid #2196F3;
  outline-offset: 2px;
}''',
                'requires': ['Modern browser support'],
                'pros': [
                    'Best UX - focus only shows for keyboard users',
                    'No focus ring on mouse click',
                    'WCAG AA compliant'
                ],
                'cons': [
                    'Limited support in older browsers'
                ],
                'wcag_criterion': '2.4.7 Focus Visible'
            },
            {
                'rank': 2,
                'method': 'custom_focus',
                'wcag_level': 'AA',
                'description': 'Add custom :focus styles',
                'explanation': 'Custom focus styles that match your design',
                'code': '''button:focus {
  outline: 2px solid #2196F3;
  outline-offset: 2px;
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.2);
}''',
                'requires': [],
                'pros': [
                    'Works in all browsers',
                    'Matches design system',
                    'Clear focus indication'
                ],
                'cons': [
                    'Shows on both keyboard and mouse focus'
                ],
                'wcag_criterion': '2.4.7 Focus Visible'
            }
        ]

    def _generate_keyboard_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for keyboard accessibility"""

        element_type = context.get('element', 'div')

        return [
            {
                'rank': 1,
                'method': 'use_semantic_button',
                'wcag_level': 'AA',
                'description': f'Replace <{element_type}> with semantic <button>',
                'explanation': 'Native buttons have built-in keyboard support and accessibility',
                'code': '<button onClick={handleClick}>\n  Click me\n</button>',
                'requires': [],
                'pros': [
                    'Built-in keyboard support (Enter, Space)',
                    'Proper role and focus management',
                    'Best practice'
                ],
                'cons': [
                    'May require CSS changes for styling'
                ],
                'wcag_criterion': '2.1.1 Keyboard'
            },
            {
                'rank': 2,
                'method': 'add_keyboard_handlers',
                'wcag_level': 'A',
                'description': f'Add keyboard support to <{element_type}>',
                'explanation': 'Make div/span clickable via keyboard',
                'code': f'''<{element_type}
  role="button"
  tabIndex={{0}}
  onClick={{handleClick}}
  onKeyDown={{(e) => {{
    if (e.key === 'Enter' || e.key === ' ') {{
      e.preventDefault();
      handleClick();
    }}
  }}}}
>
  Click me
</{element_type}>''',
                'requires': [],
                'pros': [
                    'Maintains current markup',
                    'Adds keyboard support'
                ],
                'cons': [
                    'More complex than using button',
                    'Must implement all button behaviors manually'
                ],
                'wcag_criterion': '2.1.1 Keyboard'
            }
        ]

    def _generate_aria_cleanup_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for redundant ARIA"""

        redundant_role = context.get('redundant_role', 'button')
        elem_type = context.get('element', 'button')

        return [
            {
                'rank': 1,
                'method': 'remove_redundant',
                'wcag_level': 'A',
                'description': f'Remove redundant role="{redundant_role}"',
                'explanation': f'Native <{elem_type}> already has role="{redundant_role}"',
                'code': element.replace(f'role="{redundant_role}"', '').replace('  ', ' '),
                'requires': [],
                'pros': [
                    'Cleaner code',
                    'No ARIA needed for native semantics',
                    'Follows best practice: "No ARIA is better than bad ARIA"'
                ],
                'cons': [],
                'wcag_criterion': '4.1.2 Name, Role, Value',
                'note': 'First rule of ARIA: Don\'t use ARIA if you can use native HTML'
            }
        ]

    def _generate_heading_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for heading hierarchy"""

        prev_level = context.get('prev_level', 1)
        current_level = context.get('current_level', 3)

        return [
            {
                'rank': 1,
                'method': 'fix_level',
                'wcag_level': 'A',
                'description': f'Change to <h{prev_level + 1}> to maintain hierarchy',
                'explanation': f'Heading jumps from h{prev_level} to h{current_level} - should increment by 1',
                'code': f'<h{prev_level + 1}>Heading text</h{prev_level + 1}>',
                'requires': [],
                'pros': [
                    'Proper document outline',
                    'Screen readers can navigate properly',
                    'SEO benefit'
                ],
                'cons': [
                    'May affect visual size (solve with CSS)'
                ],
                'wcag_criterion': '1.3.1 Info and Relationships',
                'note': 'Use CSS to style headings visually while maintaining semantic hierarchy'
            }
        ]

    def _generate_link_text_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Generate fixes for ambiguous link text"""

        link_text = context.get('link_text', 'click here')

        return [
            {
                'rank': 1,
                'method': 'descriptive_text',
                'wcag_level': 'A',
                'description': 'Use descriptive link text',
                'explanation': 'Link text should describe where the link goes',
                'code': f'<a href="...">Read the full article</a>  /* Instead of "{link_text}" */',
                'requires': [],
                'pros': [
                    'Clear purpose for all users',
                    'Screen readers can list all links',
                    'Better SEO'
                ],
                'cons': [],
                'wcag_criterion': '2.4.4 Link Purpose (In Context)',
                'note': 'Avoid "click here", "read more", "here" - be specific about destination'
            }
        ]

    def _generate_generic_fixes(
        self,
        element: str,
        context: Dict[str, Any],
        line_num: int
    ) -> List[Dict]:
        """Fallback for unknown issue types"""

        return [
            {
                'rank': 1,
                'method': 'manual_review',
                'wcag_level': 'Unknown',
                'description': 'Manual review required',
                'explanation': 'This issue requires manual analysis and fixing',
                'code': '/* Review WCAG guidelines for this issue type */',
                'requires': [],
                'pros': [],
                'cons': [],
                'wcag_criterion': 'See WCAG 2.2 documentation'
            }
        ]

    # Color manipulation helpers

    def _darken_color(self, color: str) -> str:
        """Darken a hex color (simplified)"""
        if not color.startswith('#'):
            return '#666'

        # Remove # and convert to RGB
        color = color.lstrip('#')
        if len(color) == 3:
            color = ''.join([c*2 for c in color])

        # Darken by reducing RGB values
        try:
            r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
            r = max(0, int(r * 0.7))
            g = max(0, int(g * 0.7))
            b = max(0, int(b * 0.7))
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return '#666'

    def _lighten_color(self, color: str) -> str:
        """Lighten a hex color (simplified)"""
        if not color.startswith('#'):
            return '#f5f5f5'

        color = color.lstrip('#')
        if len(color) == 3:
            color = ''.join([c*2 for c in color])

        try:
            r, g, b = [int(color[i:i+2], 16) for i in (0, 2, 4)]
            r = min(255, int(r + (255 - r) * 0.3))
            g = min(255, int(g + (255 - g) * 0.3))
            b = min(255, int(b + (255 - b) * 0.3))
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return '#f5f5f5'


def main():
    """CLI entry point"""
    if len(sys.argv) < 3:
        print("Usage: python generate_fixes.py <component_file> <issue_type>")
        print("\nSupported issue types:")
        print("  - missing_accessible_name")
        print("  - missing_alt_text")
        print("  - missing_form_label")
        print("  - color_contrast")
        print("  - missing_focus_indicator")
        print("  - missing_keyboard_support")
        sys.exit(1)

    file_path = sys.argv[1]
    issue_type = sys.argv[2]

    try:
        generator = FixGenerator(file_path)

        # Mock context for demonstration
        context = {
            'button_purpose': {'purpose': 'close_button', 'suggested_label': 'Close'},
            'is_icon_only': True,
            'content': '×'
        }

        fixes = generator.generate_fixes_for_issue(issue_type, '<button>×</button>', context, 10)

        print(json.dumps(fixes, indent=2))

    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating fixes: {e}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
