#!/usr/bin/env python3
"""Generate assets/terminal.svg - the whole intro, inside one terminal."""
from __future__ import annotations

import os
import textwrap

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "terminal.svg")

W, PAD = 940, 34
LINE = 25
FONT = 14.5
MONO = "JetBrains Mono, Menlo, Consolas, monospace"
CHARS = 92  # karakter per baris pada lebar ini

ABOUT = (
    "I'm a security enthusiast who has been poking at systems since 2011 - mostly in terminals, "
    "mostly on Linux, usually around CI pipelines and whatever is on fire that week. Somewhere along "
    "the way that turned into a decade of hands-on work in sysadmin and security engineering, but I "
    "still think of it as \"learning in public, slowly\"."
)
ABOUT2 = (
    "I like building small tools that make security less annoying: scripts that save an hour, scanners "
    "that catch the obvious things, and checklists that keep humans from being the weakest step. Most "
    "of it is quiet work - reading logs, reading code, reading documentation nobody else wants to read."
)
FOCUS = [
    ("Tinkering with", "Rust, Python, Go, and Cybersecurity Tools"),
    ("Focus", "DevSecOps, CyberSecurity Architecture, Code Review, Pentest & Vulnerability Assessment, Agentic Tooling"),
    ("Fuel", "Black tea, no sugar"),
    ("Always", "One more language, one more book, one more lab"),
]


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text: str, width: int = CHARS) -> list[str]:
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def main() -> None:
    rows: list[tuple[str, str, str]] = []   # (kind, text, color)

    rows.append(("prompt", "whoami", ""))
    rows.append(("out", "arkrwn", "#EAF1FF"))
    rows.append(("gap", "", ""))

    rows.append(("prompt", "cat about.txt", ""))
    for line in wrap(ABOUT):
        rows.append(("body", line, "#C7D6EC"))
    rows.append(("gap", "", ""))
    for line in wrap(ABOUT2):
        rows.append(("body", line, "#C7D6EC"))
    rows.append(("gap", "", ""))

    rows.append(("prompt", "cat focus.txt", ""))
    for label, value in FOCUS:
        chunks = wrap(f"{label} - {value}", CHARS)
        rows.append(("body", chunks[0], "#DCE8F8"))
        for extra in chunks[1:]:
            rows.append(("cont", extra, "#DCE8F8"))

    height = 78 + len(rows) * LINE + 46
    body = []
    y = 92
    for kind, text, color in rows:
        if kind == "gap":
            y += LINE
            continue
        if kind == "cont":
            body.append(
                f'    <text x="{PAD + 18}" y="{y}" font-family="{MONO}" font-size="{FONT}" '
                f'fill="{color}">{esc(text)}</text>'
            )
            y += LINE
            continue
        if kind == "prompt":
            body.append(
                f'    <text x="{PAD}" y="{y}" font-family="{MONO}" font-size="{FONT}" fill="#9FB6D9">'
                f'<tspan fill="#38E1C6">➜</tspan> <tspan fill="#5B8CFF">~</tspan> '
                f'<tspan fill="#EAF1FF">{esc(text)}</tspan></text>'
            )
        else:
            body.append(
                f'    <text x="{PAD}" y="{y}" font-family="{MONO}" font-size="{FONT}" '
                f'fill="{color}">{esc(text)}</text>'
            )
        y += LINE

    cursor_y = y - LINE + 5
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" role="img" aria-label="terminal with arkrwn's intro">
  <defs>
    <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0B1020"/>
      <stop offset="100%" stop-color="#121A33"/>
    </linearGradient>
    <linearGradient id="frame" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5B8CFF" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#38E1C6" stop-opacity="0.35"/>
    </linearGradient>
    <style>
      .cursor {{ animation: blink 1.1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
    </style>
  </defs>

  <rect width="{W}" height="{height}" rx="22" fill="#FFFFFF" fill-opacity="0.04"/>
  <rect x="1" y="1" width="{W - 2}" height="{height - 2}" rx="21" fill="none" stroke="url(#frame)"/>

  <rect x="1" y="1" width="{W - 2}" height="46" rx="21" fill="#FFFFFF" fill-opacity="0.05"/>
  <rect x="1" y="25" width="{W - 2}" height="22" fill="#FFFFFF" fill-opacity="0.05"/>
  <circle cx="30" cy="24" r="6" fill="#FF6B7A" fill-opacity="0.85"/>
  <circle cx="52" cy="24" r="6" fill="#FFC46B" fill-opacity="0.85"/>
  <circle cx="74" cy="24" r="6" fill="#4ED8A6" fill-opacity="0.85"/>
  <text x="{W / 2}" y="29" text-anchor="middle" font-family="{MONO}" font-size="12"
        fill="#7E93B5">arkrwn@github: ~</text>

{chr(10).join(body)}

  <rect class="cursor" x="{PAD}" y="{cursor_y}" width="9" height="14" fill="#6FE7D2"/>
</svg>
'''
    with open(OUT, "w") as fh:
        fh.write(svg)
    print(f"wrote {OUT}: {len(rows)} baris, {W}x{height}")


if __name__ == "__main__":
    main()
