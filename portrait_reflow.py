#!/usr/bin/env python3
"""
Portrait reflow: fix fonts + scale to 720px width using viewBox transform.
For files already at 720px, only fix fonts.
"""

import re
import sys
import os

SANS_FONT = 'Gulim, Noto Sans CJK KR, Arial, sans-serif'
MONO_FONT = 'Courier New, Consolas, DejaVu Sans Mono, monospace'


def fix_font_family(m):
    """Replace font-family attribute with correct Gulim/Courier New value."""
    attr_str = m.group(0)
    lower = attr_str.lower()
    if 'mono' in lower or 'courier' in lower or 'consolas' in lower:
        return f'font-family="{MONO_FONT}"'
    else:
        return f'font-family="{SANS_FONT}"'


def fix_fonts(content):
    """Fix all font-family attributes in SVG content."""
    return re.sub(
        r'font-family="[^"]+"',
        fix_font_family,
        content,
        flags=re.I
    )


def scale_to_720(content):
    """Scale SVG to width=720 using viewBox, proportional height."""
    svg_open = re.search(r'<svg\b[^>]*>', content, re.DOTALL | re.I)
    if not svg_open:
        return content, False

    tag = svg_open.group(0)

    w_m = re.search(r'\bwidth="(\d+)"', tag)
    h_m = re.search(r'\bheight="(\d+)"', tag)
    if not w_m or not h_m:
        return content, False

    orig_w = int(w_m.group(1))
    orig_h = int(h_m.group(1))

    if orig_w == 720:
        return content, False  # Already correct width

    new_h = round(orig_h * 720 / orig_w)

    # Build new SVG tag
    has_vb = 'viewBox' in tag
    new_tag = tag
    new_tag = re.sub(r'\bwidth="\d+"', f'width="720"', new_tag)
    new_tag = re.sub(r'\bheight="\d+"', f'height="{new_h}"', new_tag)
    if not has_vb:
        new_tag = new_tag.rstrip('>') + f' viewBox="0 0 {orig_w} {orig_h}">'

    content = content[:svg_open.start()] + new_tag + content[svg_open.end():]
    return content, True


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    content = fix_fonts(original)
    content, scaled = scale_to_720(content)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        action = 'scaled+font' if scaled else 'font-only'
        print(f"OK ({action}): {os.path.basename(path)}")
    else:
        print(f"SKIP (no change): {os.path.basename(path)}")


if __name__ == '__main__':
    targets = sys.argv[1:]
    if not targets:
        print("Usage: portrait_reflow.py <file> [file...]")
        sys.exit(1)
    for p in targets:
        process(p)
