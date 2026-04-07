"""Editable figure generator for the autoresearch-style worker-critic loop.

This is the single file the coding agent is expected to modify.
It renders a local SVG and PNG that explain the worker-critic pattern
for a Substack post in one glance.
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

WIDTH = 1600
HEIGHT = 900
OUTPUT_DIR = Path("artifacts/autoresearch/current")
SVG_PATH = OUTPUT_DIR / "figure.svg"
PNG_PATH = OUTPUT_DIR / "figure.png"
MANIFEST_PATH = OUTPUT_DIR / "artifact.json"


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    if len(color) != 6:
        raise ValueError(f"Expected 6-digit hex color, got {color!r}")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def rgba(color: str, opacity: float) -> str:
    r, g, b = hex_to_rgb(color)
    return f"rgba({r}, {g}, {b}, {opacity:.3f})"


def wrap_lines(text: str, width: int, font_size: int) -> list[str]:
    approx_chars = max(8, int(width / (font_size * 0.55)))
    lines: list[str] = []
    for paragraph in text.split("\n"):
        lines.extend(wrap(paragraph, width=approx_chars) or [""])
    return lines


class SVG:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.elements: list[str] = []

    def add(self, markup: str) -> None:
        self.elements.append(markup)

    def rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        *,
        fill: str,
        radius: float = 0,
        stroke: str | None = None,
        stroke_width: float = 0,
        opacity: float = 1.0,
    ) -> None:
        stroke_markup = ""
        if stroke:
            stroke_markup = f' stroke="{stroke}" stroke-width="{stroke_width}"'
        self.add(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" ry="{radius}" fill="{fill}" fill-opacity="{opacity}"{stroke_markup} />'
        )

    def circle(self, cx: float, cy: float, r: float, *, fill: str, opacity: float = 1.0) -> None:
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" fill-opacity="{opacity}" />')

    def line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        stroke: str,
        stroke_width: float,
        dasharray: str | None = None,
    ) -> None:
        dash_markup = f' stroke-dasharray="{dasharray}"' if dasharray else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" stroke-linecap="round"{dash_markup} />'
        )

    def path(
        self,
        d: str,
        *,
        stroke: str,
        stroke_width: float,
        fill: str = "none",
    ) -> None:
        self.add(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" />'
        )

    def polygon(self, points: list[tuple[float, float]], *, fill: str) -> None:
        joined = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polygon points="{joined}" fill="{fill}" />')

    def text(
        self,
        text: str,
        x: float,
        y: float,
        *,
        font_size: int,
        fill: str,
        weight: int = 400,
        max_width: int | None = None,
        line_height: float | None = None,
        align: str = "start",
        family: str = "Inter, Arial, sans-serif",
    ) -> None:
        lines = [text] if max_width is None else wrap_lines(text, max_width, font_size)
        line_height = line_height or font_size * 1.35
        anchor = {"start": "start", "middle": "middle", "end": "end"}[align]
        escaped_lines = [escape(line) for line in lines]
        if len(escaped_lines) == 1:
            self.add(
                f'<text x="{x}" y="{y}" font-family="{family}" font-size="{font_size}" '
                f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escaped_lines[0]}</text>'
            )
            return
        tspans = []
        for index, line in enumerate(escaped_lines):
            dy = "0" if index == 0 else f"{line_height}"
            tspans.append(f'<tspan x="{x}" dy="{dy}">{line}</tspan>')
        self.add(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{font_size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{"".join(tspans)}</text>'
        )

    def render(self) -> str:
        return "\n".join(
            [
                '<?xml version="1.0" encoding="UTF-8"?>',
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" height="{self.height}" viewBox="0 0 {self.width} {self.height}">',
                *self.elements,
                "</svg>",
            ]
        )


def pill(
    svg: SVG,
    x: int,
    y: int,
    width: int,
    height: int,
    label: str,
    *,
    fill: str,
    text_fill: str,
    stroke: str | None = None,
    font_size: int = 14,
) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=height / 2, stroke=stroke, stroke_width=1 if stroke else 0)
    svg.text(label, x + width / 2, y + height / 2 + 5, font_size=font_size, fill=text_fill, weight=600, align="middle")


def arrow(svg: SVG, x1: int, y1: int, x2: int, y2: int, *, color: str, width: int = 6) -> None:
    svg.line(x1, y1, x2, y2, stroke=color, stroke_width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = max(14, int(width * 2.4))
    left = (
        x2 - size * math.cos(angle) + size * 0.65 * math.sin(angle),
        y2 - size * math.sin(angle) - size * 0.65 * math.cos(angle),
    )
    right = (
        x2 - size * math.cos(angle) - size * 0.65 * math.sin(angle),
        y2 - size * math.sin(angle) + size * 0.65 * math.cos(angle),
    )
    svg.polygon([(x2, y2), left, right], fill=color)


def mini_artifact(svg: SVG, x: int, y: int, width: int, height: int, variant: int) -> None:
    svg.rect(x, y, width, height, fill="#FFFFFF", radius=18, stroke="#D8DEE8", stroke_width=1)
    pad = 12
    inner_x = x + pad
    inner_y = y + pad
    inner_w = width - pad * 2
    inner_h = height - pad * 2
    svg.rect(inner_x, inner_y, inner_w, 12, fill="#E8EEF6", radius=6)
    if variant == 1:
        svg.rect(inner_x + 4, inner_y + 26, inner_w * 0.30, 16, fill="#BFDBFE", radius=8)
        svg.rect(inner_x + inner_w * 0.40, inner_y + 26, inner_w * 0.30, 16, fill="#FDE68A", radius=8)
        svg.rect(inner_x + 4, inner_y + 54, inner_w - 8, 8, fill="#E2E8F0", radius=4)
        svg.rect(inner_x + 4, inner_y + 68, inner_w * 0.72, 8, fill="#E2E8F0", radius=4)
        box_y = inner_y + 82
        box_h = max(16, inner_h - 94)
        svg.rect(inner_x + 4, box_y, inner_w * 0.22, box_h, fill="#BAE6FD", radius=10)
        svg.rect(inner_x + inner_w * 0.32, box_y, inner_w * 0.24, box_h, fill="#DDD6FE", radius=10)
        svg.rect(inner_x + inner_w * 0.64, box_y, inner_w * 0.16, box_h, fill="#FCA5A5", radius=10)
    elif variant == 2:
        svg.rect(inner_x + 4, inner_y + 26, inner_w * 0.32, 16, fill="#93C5FD", radius=8)
        svg.rect(inner_x + inner_w * 0.42, inner_y + 26, inner_w * 0.28, 16, fill="#FCD34D", radius=8)
        svg.rect(inner_x + 4, inner_y + 54, inner_w * 0.34, max(26, inner_h * 0.44), fill="#CFFAFE", radius=12)
        svg.rect(inner_x + inner_w * 0.42, inner_y + 54, inner_w * 0.42, 20, fill="#DBEAFE", radius=10)
        svg.rect(inner_x + inner_w * 0.42, inner_y + 84, inner_w * 0.30, 14, fill="#E2E8F0", radius=7)
        svg.rect(inner_x + inner_w * 0.42, inner_y + 108, inner_w * 0.24, 10, fill="#E2E8F0", radius=5)
    else:
        svg.rect(inner_x + 4, inner_y + 26, inner_w * 0.32, 18, fill="#60A5FA", radius=9)
        svg.rect(inner_x + inner_w * 0.44, inner_y + 26, inner_w * 0.26, 18, fill="#F59E0B", radius=9)
        left_w = inner_w * 0.34
        svg.rect(inner_x + 4, inner_y + 56, left_w, max(28, inner_h * 0.40), fill="#E0F2FE", radius=14)
        right_x = inner_x + left_w + 20
        right_w = inner_x + inner_w - right_x - 4
        svg.rect(right_x, inner_y + 56, right_w, 24, fill="#DCFCE7", radius=10)
        svg.rect(right_x, inner_y + 88, max(20, right_w - 28), 15, fill="#E2E8F0", radius=7)
        svg.rect(right_x, inner_y + 112, max(18, right_w - 42), 8, fill="#BFDBFE", radius=4)


def add_bottom_card(svg: SVG, x: int, title: str, body: str) -> None:
    svg.rect(x, 748, 474, 122, fill="#FFFFFF", radius=24, stroke="#E3DED4", stroke_width=1)
    svg.text(title, x + 28, 780, font_size=22, fill="#0F172A", weight=700)
    svg.text(body, x + 28, 812, font_size=18, fill="#475569", max_width=418, line_height=25)


def build_figure() -> str:
    svg = SVG(WIDTH, HEIGHT)

    svg.rect(0, 0, WIDTH, HEIGHT, fill="#F7F1E8", radius=24)
    svg.circle(1460, 120, 220, fill=rgba("#93C5FD", 0.16))
    svg.circle(118, 786, 164, fill=rgba("#FCD34D", 0.16))
    svg.circle(760, 814, 132, fill=rgba("#C4B5FD", 0.12))

    pill(svg, 70, 44, 164, 34, "Agent Pattern", fill="#E8EEF8", text_fill="#1D4ED8", stroke="#C9D8F3")
    svg.text("Worker-Critic Pattern", 70, 112, font_size=58, fill="#0F172A", weight=800)
    svg.text(
        "A worker drafts, a critic reviews, feedback loops back into revision, and the process stops only on approval.",
        70,
        166,
        font_size=25,
        fill="#334155",
        max_width=1120,
        line_height=34,
    )

    svg.rect(60, 234, 1480, 586, fill="#FFFCF8", radius=36, stroke="#E6DDD1", stroke_width=1)
    pill(svg, 92, 258, 212, 34, "Repeat Until Approved", fill="#EEE9FF", text_fill="#6D28D9", stroke="#D8C8FF", font_size=15)
    svg.text("Same worker. Same critic. One visible loop.", 92, 322, font_size=22, fill="#475569", weight=600)

    svg.rect(112, 364, 258, 204, fill="#EEF5FF", radius=28, stroke="#C9D8F3", stroke_width=1)
    pill(svg, 138, 388, 136, 28, "Persistent Role", fill="#DCEAFE", text_fill="#1D4ED8", stroke="#BCD2F5")
    svg.text("Worker", 138, 456, font_size=34, fill="#102A43", weight=750)
    svg.text("Makes the next draft", 138, 494, font_size=20, fill="#274C77", weight=600)
    svg.text("Keeps the task and context alive", 138, 526, font_size=18, fill="#3B82F6", max_width=194, line_height=24)

    svg.rect(452, 326, 376, 270, fill="#FFFFFF", radius=30, stroke="#DFE6EE", stroke_width=1)
    pill(svg, 552, 346, 174, 28, "Artifact Across Rounds", fill="#F3F4F6", text_fill="#475569", stroke="#E5E7EB")
    svg.text("Draft gets sharper", 640, 408, font_size=31, fill="#0F172A", weight=760, align="middle")
    mini_artifact(svg, 504, 464, 118, 96, 1)
    mini_artifact(svg, 580, 438, 132, 108, 2)
    mini_artifact(svg, 660, 410, 136, 120, 3)
    svg.text("draft 1", 560, 586, font_size=16, fill="#64748B", weight=600, align="middle")
    svg.text("draft 2", 646, 586, font_size=16, fill="#64748B", weight=600, align="middle")
    svg.text("approved draft", 730, 586, font_size=16, fill="#15803D", weight=700, align="middle")

    svg.rect(920, 364, 270, 204, fill="#FFF4D9", radius=28, stroke="#F4D27A", stroke_width=1)
    pill(svg, 948, 388, 136, 28, "Persistent Role", fill="#FDE68A", text_fill="#92400E", stroke="#F3C85C")
    svg.text("Critic", 948, 456, font_size=34, fill="#7C2D12", weight=750)
    svg.text("Reviews against the rubric", 948, 494, font_size=20, fill="#92400E", weight=600)
    svg.text("Sends fixes back or says Approved", 948, 526, font_size=18, fill="#B45309", max_width=212, line_height=24)

    arrow(svg, 370, 470, 452, 470, color="#2563EB", width=8)
    pill(svg, 388, 430, 96, 28, "draft", fill="#EAF2FF", text_fill="#1D4ED8", stroke="#C9D8F3")

    arrow(svg, 828, 470, 902, 470, color="#D97706", width=8)
    pill(svg, 842, 430, 112, 28, "review", fill="#FFF4D9", text_fill="#B45309", stroke="#F4D27A")

    svg.path("M 1204 468 L 1260 412 L 1316 468 L 1260 524 Z", stroke="#CBD5E1", stroke_width=2, fill="#FFFFFF")
    svg.text("Approved?", 1260, 476, font_size=20, fill="#0F172A", weight=700, align="middle")

    arrow(svg, 1190, 468, 1204, 468, color="#D97706", width=7)

    arrow(svg, 1316, 468, 1320, 468, color="#16A34A", width=8)
    svg.text("yes", 1298, 446, font_size=16, fill="#15803D", weight=700, align="middle")

    svg.line(1260, 524, 1260, 638, stroke="#7C3AED", stroke_width=7)
    svg.line(1260, 638, 250, 638, stroke="#7C3AED", stroke_width=7)
    arrow(svg, 250, 638, 250, 568, color="#7C3AED", width=7)
    svg.text("no: targeted feedback -> revise", 752, 614, font_size=20, fill="#6D28D9", weight=700, align="middle")

    svg.rect(1320, 352, 180, 292, fill="#F2FCF5", radius=28, stroke="#B7E3C6", stroke_width=1)
    pill(svg, 1340, 378, 140, 30, "Approved Output", fill="#DCFCE7", text_fill="#166534", stroke="#B7E3C6")
    mini_artifact(svg, 1348, 434, 122, 118, 3)
    pill(svg, 1364, 578, 92, 32, "Approved", fill="#22C55E", text_fill="#F0FDF4", stroke="#4ADE80", font_size=15)
    svg.text("Loop stops here", 1410, 628, font_size=20, fill="#166534", weight=700, align="middle")

    return svg.render()


def export_png(svg_path: Path, png_path: Path) -> None:
    if shutil.which("rsvg-convert") is None:
        return
    subprocess.run(
        [
            "rsvg-convert",
            "-w",
            str(WIDTH),
            "-h",
            str(HEIGHT),
            "-o",
            str(png_path),
            str(svg_path),
        ],
        check=True,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    svg = build_figure()
    SVG_PATH.write_text(svg, encoding="utf-8")
    export_png(SVG_PATH, PNG_PATH)
    MANIFEST_PATH.write_text(
        (
            "{\n"
            '  "task": "worker-critic-pattern",\n'
            f'  "svg": "{SVG_PATH.as_posix()}",\n'
            f'  "png": "{PNG_PATH.as_posix()}",\n'
            f'  "width": {WIDTH},\n'
            f'  "height": {HEIGHT}\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    print(f"Wrote {SVG_PATH}")
    if PNG_PATH.exists():
        print(f"Wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
