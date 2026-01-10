#!/usr/bin/env python3
"""
Generate component mockups using OpenRouter AI (Gemini 3 Pro Image or FLUX.2 Pro)
Requires: OPENROUTER_API_KEY environment variable
"""

import os
import sys
import base64
import json
import argparse
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)

def load_env():
    """Load .env file if it exists"""
    env_file = Path.cwd() / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key not in os.environ:
                        os.environ[key] = value.strip('"').strip("'")

def generate_mockup(prompt: str, model: str, output_path: str) -> bool:
    """Generate component mockup using OpenRouter"""

    # Load environment variables
    load_env()

    api_key = os.getenv('OPENROUTER_API_KEY', '').strip()
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found or empty")
        print("\nTo enable visual generation:")
        print("1. Get API key: https://openrouter.ai/keys")
        print("2. Add to .env: OPENROUTER_API_KEY=your_key_here")
        print("3. Or export: export OPENROUTER_API_KEY=your_key_here")
        return False

    print(f"🎨 Generating mockup with {model}...")
    print(f"📝 Prompt: {prompt[:100]}...")

    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/flight505/storybook-assistant-plugin",
        "X-Title": "Storybook Assistant Plugin"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()

        data = response.json()

        # Extract image from response
        image_data = None

        # Try different response formats
        if 'choices' in data and len(data['choices']) > 0:
            choice = data['choices'][0]

            # Format 1: content with images array (Gemini)
            if 'message' in choice and 'content' in choice['message']:
                content = choice['message']['content']
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'image_url':
                            image_url = item.get('image_url', {}).get('url', '')
                            if image_url.startswith('data:image'):
                                image_data = image_url.split(',', 1)[1]
                                break
                elif isinstance(content, str) and content.startswith('data:image'):
                    image_data = content.split(',', 1)[1]

        if not image_data:
            print(f"❌ No image found in response")
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
            return False

        # Decode and save image
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'wb') as f:
            f.write(base64.b64decode(image_data))

        print(f"✅ Mockup saved: {output_file}")
        return True

    except requests.exceptions.Timeout:
        print("❌ Request timed out (60s). Try again or use a different model.")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        if response.status_code == 401:
            print("Check your OPENROUTER_API_KEY")
        elif response.status_code == 429:
            print("Rate limit exceeded. Wait a moment and try again.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Generate component mockups using AI"
    )
    parser.add_argument(
        'prompt',
        help='Description of the component mockup to generate'
    )
    parser.add_argument(
        '--model', '-m',
        default='google/gemini-3-pro-image-preview',
        help='OpenRouter model ID (default: google/gemini-3-pro-image-preview)'
    )
    parser.add_argument(
        '--output', '-o',
        default='mockup.png',
        help='Output file path (default: mockup.png)'
    )

    args = parser.parse_args()

    # Generate mockup
    success = generate_mockup(args.prompt, args.model, args.output)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
