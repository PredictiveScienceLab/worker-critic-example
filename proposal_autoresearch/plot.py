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
    svg.circle(x + 48, y + 42, 24, fill=rgba(accent, 0.14), stroke=rgba(accent, 0.45), stroke_width=2)
    svg.circle(x + 48, y + 42, 14, fill="#FFFFFF", stroke=rgba(accent, 0.65), stroke_width=2)
    svg.text(icon_label, x + 48, y + 49, font_size=18, fill=accent, weight=800, align="middle")
    svg.text(title, x + 92, y + 42, font_size=28, fill="#243B53", weight=800)
    svg.text(body, x + 92, y + 78, font_size=18, fill="#52667A", max_width=width - 120, line_height=24)


def feature_box(svg: SVG, x: int, y: int, width: int, height: int, *, title: str, lines: list[str], accent: str, fill: str) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=22, stroke=accent, stroke_width=2)
    svg.rect(x + 18, y + 18, 8, height - 36, fill=accent, radius=4)
    svg.text(title, x + 44, y + 38, font_size=23, fill="#243B53", weight=800)
    cursor_y = y + 74
    for line in lines:
        svg.text(line, x + 44, cursor_y, font_size=17, fill="#425466", max_width=width - 64, line_height=22)
        cursor_y += 32


def aim_card(svg: SVG, x: int, y: int, width: int, height: int, *, number: int, title: str, body: str, accent: str, fill: str) -> None:
    svg.rect(x, y, width, height, fill=fill, radius=24, stroke=accent, stroke_width=2)
    svg.circle(x + 34, y + 34, 20, fill=accent)
    svg.text(str(number), x + 34, y + 42, font_size=20, fill="#FFFFFF", weight=800, align="middle")
    svg.text(title, x + 66, y + 34, font_size=19, fill=accent, weight=800)
    svg.text(body, x + 28, y + 74, font_size=16, fill="#4B5D6E", max_width=width - 56, line_height=22)


def evidence_box(svg: SVG, x: int, y: int, width: int, height: int, *, title: str, body: str, accent: str, icon: str) -> None:
    svg.rect(x, y, width, height, fill="#FFFFFF", radius=22, stroke=accent, stroke_width=2)
    svg.text(icon, x + 30, y + 44, font_size=26, fill=accent, weight=800, align="middle")
    svg.text(title, x + 58, y + 38, font_size=24, fill=accent, weight=800)
    svg.text(body, x + 58, y + 72, font_size=17, fill="#4B5D6E", max_width=width - 84, line_height=23)


def footer_chip(svg: SVG, x: int, y: int, width: int, label: str, accent: str) -> None:
    svg.rect(x, y, width, 54, fill="#EEF3F7", radius=26, stroke="#D7E0E8", stroke_width=1)
    svg.circle(x + 26, y + 27, 12, fill=accent)
    svg.text(label, x + 56, y + 35, font_size=18, fill=accent, weight=800)


def posterior_panel(svg: SVG, x: int, y: int, width: int, height: int) -> None:
    svg.rect(x, y, width, height, fill="#F7FBFD", radius=28, stroke="#D9E6E8", stroke_width=1)
    band_y = y + height * 0.56
    band_x0 = x + 60
    band_x1 = x + width - 120
    svg.path(
        f"M {band_x0} {band_y} C {x + 220} {y + 20}, {x + 420} {y + height - 10}, {x + 620} {band_y} "
        f"S {x + width - 220} {y + 24}, {band_x1} {band_y}",
        stroke="#BFD9E9",
        stroke_width=44,
        opacity=0.9,
    )
    svg.path(
        f"M {band_x0 + 4} {band_y - 6} C {x + 224} {y + 26}, {x + 428} {y + height - 18}, {x + 624} {band_y - 6} "
        f"S {x + width - 216} {y + 30}, {band_x1 + 2} {band_y - 6}",
        stroke="#2A8F9C",
        stroke_width=16,
    )
    svg.path(
        f"M {band_x0 + 22} {band_y + 18} C {x + 232} {y + 64}, {x + 424} {y + height + 10}, {x + 618} {band_y + 18} "
        f"S {x + width - 200} {y + 54}, {band_x1 + 8} {band_y + 18}",
        stroke="#CC8A26",
        stroke_width=9,
    )
    for px in (band_x0 + 150, band_x0 + 310, band_x0 + 510):
        svg.circle(px, band_y - 4, 14, fill="#FFFFFF", stroke="#5B8FD1", stroke_width=3)
    svg.path(
        f"M {x + width - 300} {y + 164} C {x + width - 240} {y + 64}, {x + width - 180} {y + 248}, {x + width - 116} {y + 148}",
        stroke="#2D67A3",
        stroke_width=5,
        opacity=0.9,
    )
    svg.path(
        f"M {x + width - 336} {y + 154} C {x + width - 276} {y + 56}, {x + width - 216} {y + 236}, {x + width - 150} {y + 138}",
        stroke="#7BA8D6",
        stroke_width=3,
        opacity=0.6,
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
        58,
        74,
        font_size=52,
        fill="#243B53",
        weight=820,
        max_width=1560,
        line_height=58,
    )
    pill(
        svg,
        224,
        94,
        1330,
        48,
        "Goal: recover patient-specific geometry, flow, and pressure from noisy multimodal imaging, with quantified uncertainty.",
        fill="#E9EFF4",
        text_fill="#243B53",
        stroke="#D7E0E8",
        font_size=17,
    )

    svg.rect(44, 160, 1720, 742, fill="#FFFCF8", radius=34, stroke="#E8DED1", stroke_width=1)

    # Left panel.
    svg.rect(62, 206, 382, 550, fill="#FFFFFF", radius=30, stroke="#DDE5EC", stroke_width=1)
    svg.text("Clinical problem + data", 88, 250, font_size=28, fill="#243B53", weight=820)
    svg.text(
        "Clinically important flow is observed only indirectly and no single modality resolves geometry, pressure, and uncertainty.",
        88,
        294,
        font_size=18,
        fill="#5C6E7E",
        max_width=318,
        line_height=24,
    )
    modality_card(svg, 88, 332, 328, 104, title="PC-MRI", body="phase-contrast velocity", accent="#5B8FD1", icon_label="⊂")
    modality_card(svg, 88, 460, 328, 104, title="4D Flow MRI", body="3D + time, but spatial averaging", accent="#6AA176", icon_label="✳")
    modality_card(svg, 88, 588, 328, 104, title="Color Doppler Echo", body="fast, low cost, line-of-sight velocity", accent="#D47A66", icon_label="≋")
    svg.rect(88, 714, 328, 122, fill="#FFF5F1", radius=24, stroke="#E3B7AA", stroke_width=2)
    svg.text("Why the inverse problem is hard", 106, 752, font_size=22, fill="#C76652", weight=820)
    svg.text(
        "Noise, spatial averaging, unknown geometry, boundary / initial conditions, and modality misalignment make the inverse problem ill-posed.",
        106,
        790,
        font_size=17,
        fill="#6A4A42",
        max_width=292,
        line_height=22,
    )

    # Center panel.
    svg.rect(470, 186, 880, 612, fill="#FFFDF9", radius=30, stroke="#E8D7B5", stroke_width=2)
    svg.text("New engine: Information Field Theory (IFT)", 500, 250, font_size=28, fill="#243B53", weight=820)
    pill(svg, 1044, 214, 268, 40, "NEW: no repeated CFD solves", fill="#FFF3DE", text_fill="#C88820", stroke="#E8C17E", font_size=16)
    svg.text(
        "IFT combines measurement models and PDE-informed priors into one Bayesian reconstruction over fields, parameters, and uncertainty.",
        500,
        292,
        font_size=18,
        fill="#5C6E7E",
        max_width=800,
        line_height=24,
    )
    svg.text("Posterior Hamiltonian = data Hamiltonian + prior Hamiltonian", 500, 332, font_size=17, fill="#C88820", weight=820)

    feature_box(
        svg,
        500,
        366,
        252,
        138,
        title="Physics-informed priors",
        lines=["Eikonal geometry", "Continuity + Navier-Stokes", "beta for model-form error"],
        accent="#5B8FD1",
        fill="#F5FAFF",
    )
    feature_box(
        svg,
        774,
        366,
        252,
        138,
        title="Measurement models",
        lines=["PC-MRI, 4D Flow, Echo", "modality-specific operators", "Bayesian co-registration"],
        accent="#4D9AA7",
        fill="#F2FBFA",
    )
    feature_box(
        svg,
        1048,
        366,
        252,
        138,
        title="Scalable inference",
        lines=["persistent SGLD", "amortized VI", "data-parallel GPU batches"],
        accent="#D59A39",
        fill="#FFF8EE",
    )

    posterior_panel(svg, 500, 526, 800, 148)
    pill(svg, 1132, 528, 132, 30, "posterior output", fill="#EEF2F8", text_fill="#243B53", stroke="#D7E0E8", font_size=15)
    pill(svg, 1090, 590, 130, 30, "ill-posed problems", fill="#EAF4E9", text_fill="#5E8A67", stroke="#B9D7BB", font_size=15)
    pill(svg, 1078, 632, 150, 30, "uncertainty-aware", fill="#F2E9FF", text_fill="#7E48B3", stroke="#D9C6F6", font_size=15)
    svg.text("geometry g(x,t), velocity v(x,t),", 1246, 576, font_size=15, fill="#5C6E7E")
    svg.text("pressure p(x,t), motion, uncertainty", 1246, 602, font_size=15, fill="#5C6E7E")

    aim_y = 708
    aim_card(svg, 500, aim_y, 186, 120, number=1, title="AIM 1", body="Priors, measurement operators, and co-registration.", accent="#4F8BD0", fill="#F4F9FF")
    aim_card(svg, 700, aim_y, 186, 120, number=2, title="AIM 2", body="Boundary-aware fields plus causal / Markovian dynamics.", accent="#4D9AA7", fill="#F2FBFA")
    aim_card(svg, 900, aim_y, 186, 120, number=3, title="AIM 3", body="Persistent SGLD + amortized VI for scalable joint inference.", accent="#D59A39", fill="#FFF8EE")
    aim_card(svg, 1100, aim_y, 200, 120, number=4, title="AIM 4", body="Synthetic verification, in vitro validation, and clinical demonstration.", accent="#6F9A70", fill="#F3FAF2")

    # Right panel.
    svg.rect(1380, 206, 336, 550, fill="#FFFFFF", radius=30, stroke="#DDE5EC", stroke_width=1)
    svg.text("Validation path + impact", 1406, 250, font_size=28, fill="#243B53", weight=820)
    svg.text("Synthetic truth -> phantoms -> clinical cohorts.", 1406, 294, font_size=18, fill="#5C6E7E", max_width=282, line_height=24)
    svg.rect(1408, 334, 280, 86, fill="#F4F8FC", radius=22, stroke="#D7E0E8", stroke_width=2)
    svg.text("Decision-relevant outputs", 1432, 370, font_size=21, fill="#243B53", weight=820)
    svg.text("velocity / pressure fields,", 1432, 402, font_size=16, fill="#5C6E7E")
    svg.text("confidence bounds, image analysis", 1432, 424, font_size=16, fill="#5C6E7E")

    evidence_box(svg, 1412, 446, 272, 104, title="Verification", body="Synthetic 4D Flow + Echo against known truth", accent="#5B8FD1", icon="✓")
    evidence_box(svg, 1412, 572, 272, 104, title="Validation", body="MRI / Echo phantoms benchmarked with PIV/PTV", accent="#6AA176", icon="∿")
    evidence_box(svg, 1412, 698, 272, 104, title="Demonstration", body="Clinical cohorts for risk and model comparison", accent="#D47A66", icon="+")
    arrow(svg, 1548, 550, 1548, 570, color="#4D9AA7", width=8)
    arrow(svg, 1548, 676, 1548, 696, color="#4D9AA7", width=8)

    svg.rect(1408, 824, 280, 76, fill="#FFF7E8", radius=22, stroke="#E8C17E", stroke_width=2)
    svg.text("Intended impact", 1432, 856, font_size=22, fill="#C88820", weight=820)
    svg.text("More reliable cardiovascular image interpretation", 1432, 884, font_size=15, fill="#6A5A41", max_width=238, line_height=20)

    arrow(svg, 420, 534, 470, 534, color="#C5DCE8", width=10)
    svg.text("co-register\n+ fuse", 444, 508, font_size=18, fill="#2A8F9C", weight=800, align="middle", line_height=22)

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
