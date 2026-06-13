#!/usr/bin/env python3
"""ANSI terminal capture (.svg.html, raw ANSI) -> Apple Light terminal PNG.
Parses SGR 256-color codes, maps to Apple Light, wraps in light terminal chrome
(titlebar #e8e8ed + traffic lights, inner #f0f0f0), Gulim/mono font, hi-DPI render.
Reads assets/ (RO ok), writes print_out/light_png/ (rw ok).
Usage: python3 ansi_light.py [stem1 stem2 ...]
"""
import sys, re, html as htmlmod
from pathlib import Path
from playwright.sync_api import sync_playwright

ASSETS = Path('/mnt/c/claude-auto/assets')
PNG    = Path('/mnt/c/claude-auto/print_out/light_png')
PNG.mkdir(parents=True, exist_ok=True)

SGR = re.compile(r'\x1b\[([0-9;]*)m')
OTHER_ESC = re.compile(r'\x1b\[[0-9;]*[A-HJKlhf]|\x1b\][^\x07]*\x07')  # strip non-SGR (NOT 'm' = SGR)

def map_fg(code):
    if code is None:                       return '#1d1d1f'
    if isinstance(code, str):              return code
    if code in (15,231,255,254,253,252,7): return '#1d1d1f'   # white/light text -> ink
    if code in (250,251,249,248,247,246,245,244,243,242,241,240,8): return '#7a7a7a'  # gray -> muted
    return '#0066cc'                       # any colored fg -> Action Blue

def char_color(c):
    """Box-drawing frames -> neutral; bar-chart block elements -> Apple Light."""
    o = ord(c)
    if 0x2500 <= o <= 0x257f: return '#f0f0f0'        # ─│╭╮╰╯ box frame -> hide into bg (Mac chrome is the only frame; avoids double-line)
    if 0x2580 <= o <= 0x259f:
        if 0x2591 <= o <= 0x2593: return '#c7c7cc'   # ░▒▓ shade = empty track
        return '#0066cc'                              # █ fill = Action Blue
    return None

def esc(s): return htmlmod.escape(s)

def convert_ansi(text):
    # strip non-SGR escapes first (cursor moves, OSC, etc.)
    text = OTHER_ESC.sub('', text)
    out = []; fg = None; bold = False; pos = 0
    def emit(seg):
        if not seg: return
        i = 0
        while i < len(seg):
            cc = char_color(seg[i])
            j = i
            while j < len(seg) and char_color(seg[j]) == cc: j += 1
            run = seg[i:j]
            color = cc if cc else map_fg(fg)
            style = f'color:{color}'
            if bold and cc is None: style += ';font-weight:bold'
            out.append(f'<span style="{style}">{esc(run)}</span>')
            i = j
    for m in SGR.finditer(text):
        emit(text[pos:m.start()])
        parts = (m.group(1) or '0').split(';')
        i = 0
        while i < len(parts):
            c = parts[i]
            if c in ('', '0'):  fg = None; bold = False
            elif c == '1':      bold = True
            elif c == '22':     bold = False
            elif c == '38' and i+2 < len(parts) and parts[i+1] == '5': fg = int(parts[i+2]); i += 2
            elif c == '48' and i+2 < len(parts) and parts[i+1] == '5': i += 2  # bg ignored (unified #f0f0f0)
            elif c == '39':     fg = None
            elif c == '49':     pass
            elif c.isdigit() and 90 <= int(c) <= 97:
                fg = '#1d1d1f' if int(c) == 97 else ('#7a7a7a' if int(c) == 90 else '#0066cc')
            elif c.isdigit() and 30 <= int(c) <= 37:
                fg = '#1d1d1f' if int(c) in (30,37) else '#0066cc'
            i += 1
        pos = m.end()
    emit(text[pos:])
    return ''.join(out)

TITLES = {
    '03-1-tmux-panes':'tmux list-panes', '03-1-tmux-sessions':'tmux ls',
    '04-2-settings-json-hooks':'settings.json — hooks',
    '04-2-settings-json-plugins':'settings.json — plugins',
    '04-2-settings-json-marketplaces':'settings.json — marketplaces',
    '04-3-server-mode':'claude --server',
    '06-4-rtk-gain':'rtk gain', '06-4-rtk-version':'rtk --version',
}

def page_html(spans, title):
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8"/></head>
<body style="margin:0;background:#f5f5f7;padding:30px;display:inline-block;">
<div style="background:#f0f0f0;border:1px solid #e0e0e0;border-radius:11px;overflow:hidden;display:inline-block;box-shadow:0 1px 4px rgba(0,0,0,0.06);">
<div style="background:#e8e8ed;height:34px;display:flex;align-items:center;padding:0 14px;box-sizing:border-box;">
<span style="width:11px;height:11px;border-radius:50%;background:#ff5f57;display:inline-block;margin-right:7px;"></span>
<span style="width:11px;height:11px;border-radius:50%;background:#febc2e;display:inline-block;margin-right:7px;"></span>
<span style="width:11px;height:11px;border-radius:50%;background:#28c840;display:inline-block;"></span>
<span style="margin-left:16px;color:#7a7a7a;font-family:Gulim,'Noto Sans CJK KR',sans-serif;font-size:12.5px;">{esc(title)}</span>
</div>
<pre style="margin:0;padding:16px 20px;background:#f0f0f0;color:#1d1d1f;font-family:'DejaVu Sans Mono','GulimChe','Noto Sans Mono CJK KR','Noto Sans CJK KR','Noto Sans KR',monospace;font-size:13px;line-height:1.45;white-space:pre;">{spans}</pre>
</div></body></html>'''

names = sys.argv[1:] or list(TITLES)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(device_scale_factor=2)
    for n in names:
        raw = (ASSETS / f'{n}.svg.html').read_text(encoding='utf-8', errors='replace')
        html = page_html(convert_ansi(raw), TITLES.get(n, n))
        pg = ctx.new_page()
        pg.set_viewport_size({'width': 1400, 'height': 900})
        pg.set_content(html, wait_until='networkidle')
        pg.wait_for_timeout(300)
        body = pg.query_selector('body')
        body.screenshot(path=str(PNG / f'{n}.png'))
        pg.close()
        print(f'OK {n}')
    b.close()
print('DONE')
