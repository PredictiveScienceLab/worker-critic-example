"""Editable proposal master-figure generator for autoresearch.

This is the single file the coding agent is expected to modify.
It renders a wide SVG and PNG for the proposal in `inputs/project_description.tex`.
"""

from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parent.parent
WIDTH = 1800
HEIGHT = 1020
OUTPUT_DIR = REPO_ROOT / "artifacts" / "autoresearch-proposal" / "current"
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
    approx_chars = max(8, int(width / (font_size * 0.56)))
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

    def circle(self, cx: float, cy: float, r: float, *, fill: str, opacity: float = 1.0, stroke: str | None = None, stroke_width: float = 0) -> None:
        stroke_markup = ""
        if stroke:
            stroke_markup = f' stroke="{stroke}" stroke-width="{stroke_width}"'
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" fill-opacity="{opacity}"{stroke_markup} />')

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
        opacity: float = 1.0,
    ) -> None:
        dash_markup = f' stroke-dasharray="{dasharray}"' if dasharray else ""
        self.add(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-opacity="{opacity}" '
            f'stroke-width="{stroke_width}" stroke-linecap="round"{dash_markup} />'
        )

    def path(self, d: str, *, stroke: str, stroke_width: float, fill: str = "none", opacity: float = 1.0) -> None:
        self.add(
            f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-opacity="{opacity}" '
            f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round" />'
        )

    def polygon(self, points: list[tuple[float, float]], *, fill: str, opacity: float = 1.0) -> None:
        joined = " ".join(f"{x},{y}" for x, y in points)
        self.add(f'<polygon points="{joined}" fill="{fill}" fill-opacity="{opacity}" />')

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
        line_height = line_height or font_size * 1.32
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


def pill(svg: SVG, x: int, y: int, width: int, height: int, label: str, *, fill: str, text_fill: str, stroke: str | None = None, font_size: int = 15) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=height / 2, stroke=stroke, stroke_width=1 if stroke else 0)
    svg.text(label, x + width / 2, y + height / 2 + 5, font_size=font_size, fill=text_fill, weight=700, align="middle")


def arrow(svg: SVG, x1: int, y1: int, x2: int, y2: int, *, color: str, width: int = 6) -> None:
    svg.line(x1, y1, x2, y2, stroke=color, stroke_width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = max(14, int(width * 2.5))
    left = (
        x2 - size * math.cos(angle) + size * 0.65 * math.sin(angle),
        y2 - size * math.sin(angle) - size * 0.65 * math.cos(angle),
    )
    right = (
        x2 - size * math.cos(angle) - size * 0.65 * math.sin(angle),
        y2 - size * math.sin(angle) + size * 0.65 * math.cos(angle),
    )
    svg.polygon([(x2, y2), left, right], fill=color)


def modality_card(svg: SVG, x: int, y: int, width: int, height: int, *, title: str, body: str, accent: str, icon_label: str) -> None:
    svg.rect(x, y, width, height, fill="#FFFFFF", radius=26, stroke=accent, stroke_width=2)
    svg.circle(x + 44, y + 38, 22, fill=rgba(accent, 0.14), stroke=rgba(accent, 0.45), stroke_width=2)
    svg.circle(x + 44, y + 38, 13, fill="#FFFFFF", stroke=rgba(accent, 0.65), stroke_width=2)
    svg.text(icon_label, x + 44, y + 44, font_size=16, fill=accent, weight=800, align="middle")
    svg.text(title, x + 82, y + 40, font_size=23, fill="#243B53", weight=800)
    svg.text(body, x + 82, y + 70, font_size=16, fill="#52667A", max_width=width - 108, line_height=19)


def feature_box(svg: SVG, x: int, y: int, width: int, height: int, *, title: str, lines: list[str], accent: str, fill: str) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=22, stroke=accent, stroke_width=2)
    svg.rect(x + 18, y + 18, 8, height - 36, fill=accent, radius=4)
    title_lines = wrap_lines(title, width - 68, 19)
    title_y = y + 36
    for index, line in enumerate(title_lines):
        svg.text(line, x + 44, title_y + index * 22, font_size=19, fill="#243B53", weight=800)
    cursor_y = y + 48 + len(title_lines) * 22
    for line in lines:
        for wrapped_line in wrap_lines(line, width - 68, 15):
            svg.text(wrapped_line, x + 44, cursor_y, font_size=15, fill="#425466", max_width=width - 68, line_height=18)
            cursor_y += 18
        cursor_y += 5


def aim_card(svg: SVG, x: int, y: int, width: int, height: int, *, number: int, title: str, body: str, accent: str, fill: str) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=24, stroke=accent, stroke_width=2)
    svg.circle(x + 32, y + 32, 18, fill=accent)
    svg.text(str(number), x + 32, y + 39, font_size=18, fill="#FFFFFF", weight=800, align="middle")
    svg.text(title, x + 60, y + 34, font_size=18, fill=accent, weight=800, max_width=width - 80)
    svg.text(body, x + 24, y + 68, font_size=14, fill="#4B5D6E", max_width=width - 48, line_height=18)


def evidence_box(svg: SVG, x: int, y: int, width: int, height: int, *, title: str, body: str, accent: str, icon: str) -> None:
    svg.rect(x, y, width, height, fill="#FFFFFF", radius=22, stroke=accent, stroke_width=2)
    svg.text(icon, x + 28, y + 42, font_size=24, fill=accent, weight=800, align="middle")
    svg.text(title, x + 54, y + 36, font_size=22, fill=accent, weight=800)
    svg.text(body, x + 54, y + 66, font_size=16, fill="#4B5D6E", max_width=width - 78, line_height=20)


def footer_chip(svg: SVG, x: int, y: int, width: int, label: str, accent: str) -> None:
    svg.rect(x, y, width, 54, fill="#EEF3F7", radius=26, stroke="#D7E0E8", stroke_width=1)
    svg.circle(x + 26, y + 27, 12, fill=accent)
    svg.text(label, x + 56, y + 35, font_size=18, fill=accent, weight=800)


def tag_chip(
    svg: SVG,
    x: float,
    y: float,
    width: float,
    label: str,
    *,
    accent: str,
    fill: str | None = None,
    font_size: int = 13,
) -> None:
    chip_fill = fill or rgba(accent, 0.10)
    svg.rect(x, y, width, 30, fill=chip_fill, radius=15, stroke=rgba(accent, 0.26), stroke_width=1)
    svg.circle(x + 16, y + 15, 5, fill=accent)
    svg.text(label, x + 30, y + 20, font_size=font_size, fill=accent, weight=820, max_width=int(width - 34))


def engine_strip(svg: SVG, x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#FFF9F0", radius=24, stroke="#E7DCC8", stroke_width=1.5)
    cells = [
        ("Physics priors", "Eikonal geometry and Navier-Stokes-informed fields", "#5B8FD1"),
        ("Measurement operators", "PC-MRI, 4D Flow MRI, Echo, plus co-registration", "#4D9AA7"),
        ("Posterior inference", "Persistent SGLD and amortized VI at GPU scale", "#D59A39"),
    ]
    cell_width = width / len(cells)
    for index, (title, body, accent) in enumerate(cells):
        cell_x = x + index * cell_width
        if index:
            svg.line(cell_x, y + 18, cell_x, y + height - 18, stroke="#E3E7EB", stroke_width=1.2)
        svg.rect(cell_x + 20, y + 18, 72, 6, fill=accent, radius=3)
        svg.text(title, cell_x + 20, y + 50, font_size=21, fill="#243B53", weight=820, max_width=int(cell_width - 40), line_height=22)
        svg.text(body, cell_x + 20, y + 82, font_size=15, fill="#52667A", max_width=int(cell_width - 40), line_height=20)


def aim_band(svg: SVG, x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#FFFFFF", radius=26, stroke="#DDE5EC", stroke_width=1.5)
    aims = [
        ("Formulate reconstruction", "Priors, operators, co-registration", "#4F8BD0", "#F4F9FF"),
        ("Parameterize dynamics", "Time-evolving fields", "#4D9AA7", "#F2FBFA"),
        ("Scale posterior inference", "Persistent SGLD + amortized VI", "#D59A39", "#FFF8EE"),
        ("Verify, validate, demonstrate", "Synthetic, in vitro, clinical data", "#6F9A70", "#F3FAF2"),
    ]
    cell_width = width / len(aims)
    for index, (title, body, accent, fill) in enumerate(aims, start=1):
        cell_x = x + (index - 1) * cell_width
        if index > 1:
            svg.line(cell_x, y + 18, cell_x, y + height - 18, stroke="#E3E7EB", stroke_width=1.2)
        svg.rect(cell_x + 10, y + 10, cell_width - 20, height - 20, fill=fill, radius=18)
        svg.circle(cell_x + 32, y + 30, 13, fill=accent)
        svg.text(str(index), cell_x + 32, y + 35, font_size=13, fill="#FFFFFF", weight=820, align="middle")
        svg.text(f"Specific Aim {index}", cell_x + 52, y + 27, font_size=12, fill=accent, weight=820)
        svg.text(title, cell_x + 22, y + 60, font_size=16, fill="#243B53", weight=820, max_width=int(cell_width - 44), line_height=18)
        svg.text(body, cell_x + 22, y + 94, font_size=13, fill="#52667A", max_width=int(cell_width - 44), line_height=16)


def posterior_panel(svg: SVG, x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#F7FBFD", radius=28, stroke="#D9E6E8", stroke_width=1)
    tag_chip(svg, x + 22, y + 20, 122, "Geometry", accent="#4F8BD0", fill="#EEF4FF")
    tag_chip(svg, x + 156, y + 20, 96, "Flow", accent="#2A8F9C", fill="#ECF9F7")
    tag_chip(svg, x + 264, y + 20, 112, "Pressure", accent="#D18A21", fill="#FFF5E6")
    tag_chip(svg, x + 388, y + 20, 132, "Uncertainty", accent="#8E71C8", fill="#F5EEFF")

    upper_path = (
        f"M {x + 88} {y + 114} C {x + 238} {y + 62}, {x + 402} {y + 150}, {x + 548} {y + 120} "
        f"S {x + width - 174} {y + 62}, {x + width - 98} {y + 100}"
    )
    lower_path = (
        f"M {x + 94} {y + 154} C {x + 244} {y + 118}, {x + 406} {y + 206}, {x + 554} {y + 166} "
        f"S {x + width - 180} {y + 112}, {x + width - 104} {y + 144}"
    )
    center_path = (
        f"M {x + 92} {y + 134} C {x + 242} {y + 90}, {x + 404} {y + 180}, {x + 550} {y + 142} "
        f"S {x + width - 178} {y + 90}, {x + width - 100} {y + 122}"
    )
    svg.path(center_path, stroke="#B98EDC", stroke_width=72, opacity=0.17)
    svg.path(center_path, stroke="#D9EEF4", stroke_width=46, opacity=0.98)
    svg.path(upper_path, stroke="#5B8FD1", stroke_width=4.5, opacity=0.95)
    svg.path(lower_path, stroke="#5B8FD1", stroke_width=4.5, opacity=0.95)
    svg.path(
        f"M {x + 90} {y + 96} C {x + 240} {y + 48}, {x + 400} {y + 134}, {x + 548} {y + 106} "
        f"S {x + width - 170} {y + 50}, {x + width - 94} {y + 88}",
        stroke="#B98EDC",
        stroke_width=2.5,
        opacity=0.55,
    )
    svg.path(
        f"M {x + 98} {y + 172} C {x + 248} {y + 130}, {x + 408} {y + 220}, {x + 556} {y + 182} "
        f"S {x + width - 184} {y + 126}, {x + width - 108} {y + 160}",
        stroke="#B98EDC",
        stroke_width=2.5,
        opacity=0.55,
    )

    arrow(svg, x + 170, y + 132, x + 294, y + 128, color="#2A8F9C", width=7)
    arrow(svg, x + 362, y + 144, x + 498, y + 146, color="#2A8F9C", width=7)
    arrow(svg, x + 564, y + 144, x + 700, y + 126, color="#2A8F9C", width=7)

    svg.path(
        f"M {x + 148} {y + 176} C {x + 310} {y + 152}, {x + 492} {y + 212}, {x + 660} {y + 182} "
        f"S {x + width - 168} {y + 132}, {x + width - 110} {y + 150}",
        stroke="#D18A21",
        stroke_width=8,
        opacity=0.92,
    )
    for cx, cy, radius, opacity in [
        (x + 192, y + 172, 18, 0.24),
        (x + 386, y + 174, 14, 0.18),
        (x + 592, y + 160, 11, 0.14),
    ]:
        svg.circle(cx, cy, radius, fill=rgba("#D18A21", opacity))
        svg.circle(cx, cy, radius * 0.54, fill="#FFFFFF", stroke=rgba("#D18A21", 0.55), stroke_width=2)

    svg.path(
        f"M {x + width - 272} {y + 164} C {x + width - 238} {y + 114}, {x + width - 202} {y + 184}, {x + width - 162} {y + 160}",
        stroke="#2D67A3",
        stroke_width=4,
        opacity=0.88,
    )
    svg.path(
        f"M {x + width - 260} {y + 178} C {x + width - 226} {y + 130}, {x + width - 190} {y + 198}, {x + width - 152} {y + 174}",
        stroke="#7BA8D6",
        stroke_width=3,
        opacity=0.70,
    )


def build_figure() -> str:
    svg = SVG(WIDTH, HEIGHT)

    svg.rect(0, 0, WIDTH, HEIGHT, fill="#F5F1E8", radius=24)
    svg.circle(1660, 120, 220, fill=rgba("#C9D9EB", 0.36))
    svg.circle(110, 880, 170, fill=rgba("#F4D28C", 0.26))
    svg.circle(860, 930, 110, fill=rgba("#C7B5F3", 0.16))
    svg.path("M 58 118 C 450 76, 1010 150, 1734 74", stroke="#DDE5EC", stroke_width=16, opacity=0.7)

    svg.text(
        "Multimodal Bayesian Reconstruction of Cardiovascular Hemodynamics",
        54,
        68,
        font_size=44,
        fill="#243B53",
        weight=820,
        max_width=1700,
        line_height=48,
    )
    pill(
        svg,
        280,
        92,
        1240,
        42,
        "Goal: infer patient-specific cardiac structure, flow, and pressure from multimodal imaging with quantified uncertainty.",
        fill="#E9EFF4",
        text_fill="#243B53",
        stroke="#D7E0E8",
        font_size=16,
    )

    svg.rect(44, 150, 1720, 748, fill="#FFFCF8", radius=34, stroke="#E8DED1", stroke_width=1)

    # Left panel.
    svg.rect(62, 184, 384, 692, fill="#FFFFFF", radius=30, stroke="#DDE5EC", stroke_width=1)
    svg.text("Clinical problem + data", 86, 228, font_size=28, fill="#243B53", weight=820)
    svg.text(
        "No single modality resolves cardiac geometry, flow, pressure, and uncertainty on its own.",
        86,
        268,
        font_size=17,
        fill="#5C6E7E",
        max_width=324,
        line_height=22,
    )
    modality_card(svg, 86, 316, 332, 108, title="PC-MRI", body="phase-contrast velocity", accent="#5B8FD1", icon_label="P")
    modality_card(svg, 86, 438, 332, 108, title="4D Flow MRI", body="3D + time, but spatially averaged", accent="#6AA176", icon_label="4")
    modality_card(svg, 86, 560, 332, 108, title="Color Doppler Echo", body="fast, low-cost line-of-sight velocity", accent="#D47A66", icon_label="E")
    svg.rect(86, 694, 332, 146, fill="#FFF5F1", radius=24, stroke="#E3B7AA", stroke_width=2)
    svg.text("Why the inverse problem is hard", 106, 732, font_size=21, fill="#C76652", weight=820)
    svg.text(
        "Noise, spatial averaging, unknown geometry, boundary conditions, and modality misalignment make inference ill-posed.",
        106,
        770,
        font_size=17,
        fill="#6A4A42",
        max_width=296,
        line_height=22,
    )

    # Center panel.
    svg.rect(462, 184, 886, 692, fill="#FFFDF9", radius=30, stroke="#E8D7B5", stroke_width=2)
    svg.text("Information Field Theory engine", 490, 228, font_size=29, fill="#243B53", weight=820)
    pill(svg, 1098, 196, 214, 36, "No repeated CFD solves", fill="#FFF3DE", text_fill="#C88820", stroke="#E8C17E", font_size=15)
    svg.text(
        "IFT fuses modality-specific measurement operators and physics-informed priors into one Bayesian posterior over time-evolving cardiovascular fields.",
        490,
        268,
        font_size=18,
        fill="#5C6E7E",
        max_width=790,
        line_height=24,
    )
    svg.rect(490, 300, 378, 38, fill="#FFF5E2", radius=19, stroke="#E8C17E", stroke_width=1.5)
    svg.text("Posterior = measurement fit + physics prior", 514, 324, font_size=16, fill="#C88820", weight=820)
    engine_strip(svg, 490, 352, 820, 110)
    svg.text("Joint posterior fields", 490, 490, font_size=18, fill="#243B53", weight=820)
    posterior_panel(svg, 490, 506, 820, 206)
    svg.text("Specific aims", 490, 734, font_size=18, fill="#243B53", weight=820)
    aim_band(svg, 490, 744, 820, 120)

    # Right panel.
    svg.rect(1370, 184, 346, 692, fill="#FFFFFF", radius=30, stroke="#DDE5EC", stroke_width=1)
    svg.text("Evidence path + impact", 1396, 228, font_size=27, fill="#243B53", weight=820)
    svg.text("Synthetic truth -> in vitro benchmarks -> clinical data.", 1396, 268, font_size=17, fill="#5C6E7E", max_width=292, line_height=22)
    svg.rect(1398, 314, 290, 108, fill="#F4F8FC", radius=22, stroke="#D7E0E8", stroke_width=2)
    svg.text("Decision-relevant outputs", 1422, 348, font_size=20, fill="#243B53", weight=820)
    tag_chip(svg, 1420, 364, 110, "Geometry", accent="#4F8BD0", fill="#EEF4FF")
    tag_chip(svg, 1542, 364, 86, "Flow", accent="#2A8F9C", fill="#ECF9F7")
    tag_chip(svg, 1420, 396, 108, "Pressure", accent="#D18A21", fill="#FFF5E6")
    tag_chip(svg, 1542, 396, 118, "Uncertainty", accent="#8E71C8", fill="#F5EEFF")

    evidence_box(svg, 1400, 442, 286, 92, title="Verification", body="Synthetic 4D Flow + Echo with ground truth", accent="#5B8FD1", icon="✓")
    evidence_box(svg, 1400, 550, 286, 92, title="Validation", body="In vitro MRI / Echo phantoms with PIV/PTV", accent="#6AA176", icon="∿")
    evidence_box(svg, 1400, 658, 286, 92, title="Demonstration", body="Clinical datasets across heart conditions", accent="#D47A66", icon="+")
    arrow(svg, 1542, 536, 1542, 548, color="#4D9AA7", width=7)
    arrow(svg, 1542, 644, 1542, 656, color="#4D9AA7", width=7)

    svg.rect(1400, 776, 286, 86, fill="#FFF7E8", radius=22, stroke="#E8C17E", stroke_width=2)
    svg.text("Intended impact", 1424, 822, font_size=21, fill="#C88820", weight=820)
    svg.text("More reliable cardiovascular image interpretation", 1424, 844, font_size=15, fill="#6A5A41", max_width=244, line_height=19)

    arrow(svg, 420, 510, 462, 510, color="#C5DCE8", width=9)
    arrow(svg, 1348, 596, 1370, 596, color="#C5DCE8", width=9)

    footer_chip(svg, 58, 918, 480, "Open-source GPU software", accent="#2A8F9C")
    footer_chip(svg, 776, 918, 520, "Benchmark datasets + reproducible code", accent="#3B73B9")
    footer_chip(svg, 1522, 918, 240, "Students + outreach", accent="#5E8A67")

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
    svg_markup = build_figure()
    SVG_PATH.write_text(svg_markup, encoding="utf-8")
    export_png(SVG_PATH, PNG_PATH)
    MANIFEST_PATH.write_text(
        (
            "{\n"
            f'  "svg": "{SVG_PATH.as_posix()}",\n'
            f'  "png": "{PNG_PATH.as_posix()}",\n'
            '  "task": "proposal-master-figure"\n'
            "}\n"
        ),
        encoding="utf-8",
    )
    print(f"Wrote {SVG_PATH}")
    if PNG_PATH.exists():
        print(f"Wrote {PNG_PATH}")


if __name__ == "__main__":
    main()
