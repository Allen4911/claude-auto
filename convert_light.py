#!/usr/bin/env python3
"""Convert dark SVG.html files to Apple Light style per LIGHT-MAP.md rules."""

import re
import sys
import os

def convert_svg(content):
    # Step 1: Process circle elements — traffic lights (r<=8) get macOS system colors
    def process_circle(m):
        c = m.group(0)
        r_m = re.search(r'\br="?(\d+(?:\.\d+)?)"?', c)
        r_val = float(r_m.group(1)) if r_m else 999
        if r_val <= 8:
            c = re.sub(r'#f38ba8', '#ff5f57', c, flags=re.I)
            c = re.sub(r'#f9e2af', '#febc2e', c, flags=re.I)
            c = re.sub(r'#a6e3a1', '#28c840', c, flags=re.I)
        else:
            c = re.sub(r'#f38ba8|#f9e2af|#a6e3a1', '#0066cc', c, flags=re.I)
        return c

    content = re.sub(r'<circle\b[^>]*(?:/>|>.*?</circle>)', process_circle,
                     content, flags=re.DOTALL | re.I)

    # Step 2: Remaining traffic light colors (non-circle context) → #0066cc
    content = re.sub(r'#f38ba8', '#0066cc', content, flags=re.I)
    content = re.sub(r'#f9e2af', '#0066cc', content, flags=re.I)
    content = re.sub(r'#a6e3a1', '#0066cc', content, flags=re.I)

    # Step 3: Catppuccin base colors
    content = re.sub(r'#1e1e2e', '#f5f5f7', content, flags=re.I)
    content = re.sub(r'#181825', '#f0f0f0', content, flags=re.I)
    content = re.sub(r'#11111b', '#f0f0f0', content, flags=re.I)
    content = re.sub(r'#313244', '#ffffff', content, flags=re.I)
    content = re.sub(r'#45475a', '#e8e8ed', content, flags=re.I)
    content = re.sub(r'#585b70', '#c7c7cc', content, flags=re.I)
    content = re.sub(r'#cdd6f4', '#1d1d1f', content, flags=re.I)
    content = re.sub(r'#a6adc8', '#7a7a7a', content, flags=re.I)

    # Step 4: Catppuccin accent colors → #0066cc
    for ac in ['#89b4fa', '#cba6f7', '#94e2d5', '#f5c2e7', '#fab387']:
        content = re.sub(ac, '#0066cc', content, flags=re.I)

    # Step 5: Tailwind Slate background/surface colors
    content = re.sub(r'#0f172a', '#f5f5f7', content, flags=re.I)
    for dark in ['#1e293b', '#172035', '#162032', '#1e3a5f',
                 '#064e3b', '#0c2a1a', '#0f2d1b', '#1c3a2e', '#1e2d1b',
                 '#2d0a0a', '#450a0a', '#2d1b1b', '#451a1a', '#3b1f5c',
                 '#2d1020', '#1e1b2d', '#2d1e00', '#2d1b0e', '#78350f']:
        content = re.sub(dark, '#ffffff', content, flags=re.I)
    content = re.sub(r'#334155', '#e8e8ed', content, flags=re.I)
    content = re.sub(r'#475569', '#c7c7cc', content, flags=re.I)
    content = re.sub(r'#64748b', '#7a7a7a', content, flags=re.I)
    content = re.sub(r'#6e7681', '#7a7a7a', content, flags=re.I)
    content = re.sub(r'#94a3b8', '#7a7a7a', content, flags=re.I)
    content = re.sub(r'#e2e8f0', '#1d1d1f', content, flags=re.I)

    # Step 6: Tailwind Slate accent colors → #0066cc
    for ac in [
        '#22c55e', '#4ade80', '#86efac', '#10b981', '#6ee7b7', '#34d399', '#059669',
        '#ef4444', '#fca5a5', '#f87171',
        '#3b82f6', '#60a5fa', '#93c5fd', '#7dd3fc', '#bfdbfe', '#1da1f2', '#1e40af',
        '#8b5cf6', '#a78bfa', '#c4b5fd', '#7c3aed',
        '#f59e0b', '#fbbf24', '#fde68a',
        '#ec4899', '#fbcfe8', '#f9a8d4', '#f472b6',
        '#5865f2', '#818cf8',
    ]:
        content = re.sub(ac, '#0066cc', content, flags=re.I)

    # Step 7: Font replacement
    content = re.sub(
        r'Noto Sans Mono CJK KR,?\s*DejaVu Sans Mono[^"\'<>]*',
        'Courier New, Consolas, DejaVu Sans Mono, monospace',
        content, flags=re.I
    )
    content = re.sub(
        r'Noto Sans CJK KR,?\s*DejaVu Sans[^"\'<>]*',
        'Gulim, Noto Sans CJK KR, Arial, sans-serif',
        content, flags=re.I
    )

    return content


def check_dark_remaining(content):
    """Return list of dark colors still found in content."""
    dark_patterns = [
        '#1e1e2e', '#0f172a', '#181825', '#11111b', '#313244', '#45475a',
        '#585b70', '#cdd6f4', '#a6adc8', '#89b4fa', '#a6e3a1', '#fab387',
        '#f9e2af', '#cba6f7', '#94e2d5', '#f5c2e7', '#f38ba8',
        '#1e293b', '#172035', '#162032', '#1e3a5f', '#334155', '#475569',
        '#94a3b8', '#e2e8f0',
    ]
    found = []
    for p in dark_patterns:
        if re.search(p, content, re.I):
            found.append(p)
    return found


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: convert_light.py <file> [file...]")
        sys.exit(1)

    for path in sys.argv[1:]:
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()
        converted = convert_svg(original)
        remaining = check_dark_remaining(converted)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(converted)
        status = "OK" if not remaining else f"WARN:{','.join(remaining)}"
        print(f"{os.path.basename(path)}: {status}")
