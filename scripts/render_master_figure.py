from __future__ import annotations

import argparse
import math
import shutil
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


W = 1950
H = 900

BG = "#F7F6F1"
INK = "#163141"
MUTED = "#5C6D78"
NAVY = "#0D3B66"
TEAL = "#0F8B8D"
SKY = "#6CA6C1"
GOLD = "#D89B34"
RUST = "#D05C42"
LEAF = "#7AA95C"
CARD = "#FFFDFC"
LINE = "#D8DED8"


def svg_text(text: str) -> str:
    return escape(text)


def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str = "none", stroke_width: int = 1, rx: int = 28, extra: str = "") -> str:
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" {extra}/>'
    )


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, stroke_width: int = 2, dash: str | None = None, marker_end: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    marker_attr = f' marker-end="url(#{marker_end})"' if marker_end else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        f'stroke="{stroke}" stroke-width="{stroke_width}" stroke-linecap="round"{dash_attr}{marker_attr}/>'
    )


def path(d: str, fill: str = "none", stroke: str = "none", stroke_width: int = 1, extra: str = "") -> str:
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" {extra}/>'


def circle(cx: float, cy: float, r: float, fill: str, stroke: str = "none", stroke_width: int = 1, extra: str = "") -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" {extra}/>'


def polygon(points: list[tuple[float, float]], fill: str, stroke: str = "none", stroke_width: int = 1, extra: str = "") -> str:
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" {extra}/>'


def text(x: float, y: float, content: str, size: int, fill: str = INK, weight: int = 500, anchor: str = "start", family: str = "'Avenir Next', 'Helvetica Neue', Arial, sans-serif", extra: str = "") -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="{family}" '
        f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{svg_text(content)}</text>'
    )


def multiline_text(x: float, y: float, lines: list[str], size: int, fill: str = INK, weight: int = 500, line_gap: int = 1.3, anchor: str = "start", family: str = "'Avenir Next', 'Helvetica Neue', Arial, sans-serif") -> str:
    pieces = [
        f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="{family}" font-weight="{weight}" text-anchor="{anchor}">'
    ]
    for idx, item in enumerate(lines):
        dy = "0" if idx == 0 else f"{line_gap}em"
        pieces.append(f'<tspan x="{x}" dy="{dy}">{svg_text(item)}</tspan>')
    pieces.append("</text>")
    return "".join(pieces)


def chip(x: float, y: float, w: float, label: str, fill: str, text_fill: str = INK, stroke: str = "none") -> str:
    return (
        rect(x, y, w, 34, fill=fill, stroke=stroke, stroke_width=1, rx=17)
        + text(x + w / 2, y + 24, label, 16, fill=text_fill, weight=600, anchor="middle")
    )


def arrow_between(x1: float, x2: float, y: float, color: str) -> str:
    mx = (x1 + x2) / 2
    return (
        line(x1, y, x2, y, color, stroke_width=5)
        + polygon([(mx + 24, y), (mx - 8, y - 16), (mx - 8, y + 16)], fill=color)
    )


def small_check(cx: float, cy: float, color: str) -> str:
    d = f"M {cx-10} {cy} L {cx-2} {cy+8} L {cx+12} {cy-10}"
    return path(d, stroke=color, stroke_width=4, extra='stroke-linecap="round" stroke-linejoin="round"')


def modality_card(x: float, y: float, title_text: str, subtitle: str, footer: str, accent: str, icon_kind: str) -> str:
    parts = [
        rect(x, y, 370, 76, fill="#FFFFFF", stroke=LINE, stroke_width=2, rx=22, extra='filter="url(#cardShadow)"'),
        circle(x + 46, y + 38, 22, fill=accent, extra='opacity="0.15"'),
        circle(x + 46, y + 38, 22, fill="none", stroke=accent, stroke_width=2),
    ]

    if icon_kind == "pc-mri":
        parts.append(circle(x + 46, y + 38, 13, fill="url(#phaseGradient)", stroke="none"))
        parts.append(path(f"M {x+34} {y+38} C {x+39} {y+25}, {x+53} {y+51}, {x+58} {y+38}", stroke="#FFFFFF", stroke_width=2.5, extra='stroke-linecap="round"'))
    elif icon_kind == "4d-flow":
        parts.append(rect(x + 34, y + 26, 24, 24, fill="none", stroke=accent, stroke_width=2, rx=5))
        parts.append(line(x + 38, y + 49, x + 54, y + 33, accent, stroke_width=2))
        parts.append(line(x + 46, y + 26, x + 46, y + 50, accent, stroke_width=2, marker_end="tinyArrow"))
    elif icon_kind == "echo":
        parts.append(path(f"M {x+34} {y+30} L {x+53} {y+24} L {x+57} {y+34} L {x+38} {y+40} Z", fill=accent))
        parts.append(path(f"M {x+48} {y+36} Q {x+72} {y+40} {x+66} {y+59} Q {x+52} {y+56} {x+48} {y+36}", fill=accent, extra='opacity="0.18"'))
        parts.append(path(f"M {x+54} {y+39} L {x+64} {y+48}", stroke=accent, stroke_width=2.5, extra='stroke-linecap="round"'))

    parts.extend(
        [
            text(x + 84, y + 29, title_text, 22, fill=INK, weight=700),
            text(x + 84, y + 50, subtitle, 15, fill=MUTED, weight=500),
            text(x + 84, y + 67, footer, 14, fill=accent, weight=600),
        ]
    )
    return "".join(parts)


def method_box(x: float, y: float, w: float, h: float, title_text: str, body_lines: list[str], accent: str, icon: str) -> str:
    parts = [
        rect(x, y, w, h, fill="#FFFFFF", stroke=LINE, stroke_width=2, rx=26, extra='filter="url(#cardShadow)"'),
        rect(x + 20, y + 15, 50, 50, fill=accent, stroke="none", rx=16, extra='opacity="0.14"'),
    ]
    if icon == "prior":
        parts.append(path(f"M {x+34} {y+48} C {x+44} {y+26}, {x+62} {y+26}, {x+72} {y+48}", stroke=accent, stroke_width=3, extra='stroke-linecap="round"'))
        parts.append(path(f"M {x+42} {y+53} Q {x+52} {y+38} {x+62} {y+53}", stroke=accent, stroke_width=3, extra='stroke-linecap="round"'))
    elif icon == "measurement":
        parts.append(rect(x + 34, y + 31, 24, 16, fill="none", stroke=accent, stroke_width=2, rx=4))
        parts.append(line(x + 58, y + 39, x + 76, y + 39, accent, stroke_width=3, marker_end="tinyArrow"))
        parts.append(circle(x + 78, y + 39, 6, fill="none", stroke=accent, stroke_width=2))
    elif icon == "parameter":
        parts.append(path(f"M {x+36} {y+53} C {x+42} {y+27}, {x+64} {y+27}, {x+72} {y+53}", stroke=accent, stroke_width=3, extra='stroke-linecap="round"'))
        parts.append(line(x + 40, y + 42, x + 70, y + 42, accent, stroke_width=2, dash="5 5"))
    elif icon == "inference":
        parts.append(circle(x + 42, y + 42, 7, fill=accent))
        parts.append(circle(x + 58, y + 32, 7, fill=accent, extra='opacity="0.75"'))
        parts.append(circle(x + 69, y + 49, 7, fill=accent, extra='opacity="0.55"'))
        parts.append(line(x + 42, y + 42, x + 58, y + 32, accent, stroke_width=2))
        parts.append(line(x + 58, y + 32, x + 69, y + 49, accent, stroke_width=2))
    parts.append(text(x + 90, y + 31, title_text, 22, fill=INK, weight=700))
    parts.append(multiline_text(x + 90, y + 54, body_lines, 15, fill=MUTED, weight=500))
    return "".join(parts)


def aim_card(x: float, y: float, w: float, h: float, number: str, title_lines: list[str], lines: list[str], accent: str) -> str:
    parts = [
        rect(x, y, w, h, fill=CARD, stroke=LINE, stroke_width=2, rx=28, extra='filter="url(#cardShadow)"'),
        rect(x + 22, y + 20, 60, 60, fill=accent, stroke="none", rx=20),
        text(x + 52, y + 61, number, 28, fill="#FFFFFF", weight=700, anchor="middle"),
        multiline_text(x + 100, y + 40, title_lines, 21, fill=INK, weight=700, line_gap=1.1),
    ]
    body_y = y + 94
    for idx, item in enumerate(lines):
        yy = body_y + idx * 32
        parts.append(circle(x + 104, yy - 7, 5, fill=accent))
        parts.append(text(x + 122, yy, item, 16, fill=MUTED, weight=500))
    return "".join(parts)


def build_svg() -> str:
    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">')
    parts.append("<title id=\"title\">Proposal overview figure for cardiovascular hemodynamics reconstruction</title>")
    parts.append(
        "<desc id=\"desc\">Wide overview figure showing multimodal cardiovascular imaging flowing into an information field theory engine, a validation pathway, and four specific aims.</desc>"
    )
    parts.append(
        """
<defs>
  <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#FBFAF6"/>
    <stop offset="100%" stop-color="#EEF5F5"/>
  </linearGradient>
  <linearGradient id="phaseGradient" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#6CA6C1"/>
    <stop offset="50%" stop-color="#0F8B8D"/>
    <stop offset="100%" stop-color="#D89B34"/>
  </linearGradient>
  <linearGradient id="objectiveGradient" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0D3B66"/>
    <stop offset="100%" stop-color="#0F8B8D"/>
  </linearGradient>
  <linearGradient id="posteriorGradient" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#0D3B66"/>
    <stop offset="100%" stop-color="#6CA6C1"/>
  </linearGradient>
  <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">
    <feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#9AA9AE" flood-opacity="0.14"/>
  </filter>
  <marker id="tinyArrow" markerWidth="10" markerHeight="10" refX="7" refY="3.5" orient="auto">
    <polygon points="0 0, 7 3.5, 0 7" fill="#0F8B8D"/>
  </marker>
</defs>
"""
    )
    parts.append(rect(0, 0, W, H, fill="url(#bgGradient)", rx=0))
    parts.append(circle(1680, 140, 240, fill="#E4F0F1", extra='opacity="0.55"'))
    parts.append(circle(290, 760, 210, fill="#F3E8D6", extra='opacity="0.55"'))
    parts.append(path("M 60 636 C 360 560, 660 706, 954 622 S 1600 556, 1886 612", stroke="#D9E7E4", stroke_width=3, extra='stroke-linecap="round" opacity="0.8"'))
    parts.append(path("M 88 164 C 380 126, 730 216, 1120 154 S 1650 120, 1860 172", stroke="#E7EAE3", stroke_width=2, extra='stroke-linecap="round" opacity="0.9"'))

    parts.append(rect(54, 36, 1842, 100, fill="url(#objectiveGradient)", stroke="none", rx=34, extra='filter="url(#cardShadow)"'))
    parts.append(rect(82, 56, 170, 58, fill="#FFFFFF", stroke="none", rx=20, extra='opacity="0.16"'))
    parts.append(text(167, 93, "Objective", 28, fill="#FFFFFF", weight=700, anchor="middle"))
    parts.append(multiline_text(284, 74, ["Physics-informed Bayesian reconstruction", "of cardiovascular flow from multimodal imaging"], 35, fill="#FFFFFF", weight=750, line_gap=1.0))
    parts.append(text(284, 127, "Infer patient-specific geometry, velocity, pressure, and uncertainty from noisy PC-MRI, 4D Flow MRI, and Doppler Echo.", 20, fill="#EAF5F5", weight=500))

    parts.append(rect(54, 170, 424, 470, fill=CARD, stroke=LINE, stroke_width=2, rx=30, extra='filter="url(#cardShadow)"'))
    parts.append(text(86, 214, "Clinical data and bottlenecks", 28, fill=INK, weight=700))
    parts.append(text(86, 244, "Direct measurements are informative, but noisy, partial,", 18, fill=MUTED, weight=500))
    parts.append(text(86, 268, "spatially averaged, and often hard to co-register.", 18, fill=MUTED, weight=500))
    parts.append(chip(86, 288, 80, "Noisy", fill="#E9F1F3", text_fill=NAVY))
    parts.append(chip(176, 288, 84, "Partial", fill="#E9F1F3", text_fill=NAVY))
    parts.append(chip(270, 288, 112, "Averaged", fill="#F6EAD9", text_fill=GOLD))
    parts.append(chip(86, 330, 142, "Misregistered", fill="#F4E1DB", text_fill=RUST))
    parts.append(chip(238, 330, 144, "Ill-posed", fill="#E8EFE5", text_fill=LEAF))
    parts.append(modality_card(86, 368, "PC-MRI", "phase-contrast velocity images", "patient-specific but resolution-limited", NAVY, "pc-mri"))
    parts.append(modality_card(86, 454, "4D Flow MRI", "3D + time velocity measurements", "captures complex flow over the cardiac cycle", TEAL, "4d-flow"))
    parts.append(modality_card(86, 540, "Color Doppler Echo", "probe-aligned flow observations", "fast and inexpensive, line-of-sight only", GOLD, "echo"))

    parts.append(rect(504, 170, 840, 470, fill=CARD, stroke=LINE, stroke_width=2, rx=30, extra='filter="url(#cardShadow)"'))
    parts.append(text(536, 214, "Information Field Theory engine", 30, fill=INK, weight=700))
    parts.append(text(536, 244, "Bayesian inference over fields fuses data with physics without relying on a CFD solver in the loop.", 18, fill=MUTED, weight=500))
    parts.append(rect(1132, 188, 180, 38, fill="#E6F2F2", stroke="none", rx=19))
    parts.append(text(1222, 214, "No CFD solver required", 16, fill=TEAL, weight=700, anchor="middle"))

    parts.append(method_box(536, 272, 776, 62, "Physics-informed priors", ["Eikonal, continuity, Navier-Stokes, and boundary-condition Hamiltonians"], NAVY, "prior"))
    parts.append(method_box(536, 346, 776, 62, "Measurement operators + co-registration", ["Forward models for PC-MRI, 4D Flow MRI, Echo, and modality alignment"], TEAL, "measurement"))
    parts.append(method_box(536, 420, 776, 62, "Spatiotemporal parameterization", ["Adaptive spatial bases plus Markovian time evolution with initial conditions"], GOLD, "parameter"))
    parts.append(method_box(536, 494, 776, 62, "Scalable posterior inference", ["Preconditioned SGLD and amortized VI with Monte Carlo gradients and batching"], RUST, "inference"))
    parts.append(rect(640, 570, 564, 64, fill="url(#posteriorGradient)", stroke="none", rx=28, extra='filter="url(#cardShadow)"'))
    parts.append(text(922, 596, "Joint posterior over fields + parameters", 26, fill="#FFFFFF", weight=750, anchor="middle"))
    parts.append(text(922, 620, "geometry, velocity, pressure, modality transforms, and uncertainty", 17, fill="#DDF1F4", weight=500, anchor="middle"))

    parts.append(rect(1370, 170, 526, 470, fill=CARD, stroke=LINE, stroke_width=2, rx=30, extra='filter="url(#cardShadow)"'))
    parts.append(text(1402, 214, "Outputs, validation, and impact", 28, fill=INK, weight=700))
    parts.append(multiline_text(1402, 242, ["Posterior reconstructions support validation,", "comparison, and clinical interpretation."], 17, fill=MUTED, weight=500, line_gap=1.1))

    parts.append(rect(1402, 272, 462, 118, fill="#F6FBFB", stroke="#DCE7E6", stroke_width=2, rx=24))
    parts.append(path("M 1460 336 C 1498 300, 1542 290, 1590 314 S 1686 358, 1738 332 S 1816 286, 1844 316", stroke="#C9D9DB", stroke_width=36, extra='stroke-linecap="round" opacity="0.9"'))
    parts.append(path("M 1456 338 C 1496 300, 1540 292, 1588 316 S 1684 360, 1736 334 S 1816 286, 1842 318", stroke="url(#posteriorGradient)", stroke_width=18, extra='stroke-linecap="round"'))
    for offset, color in [(0, "#FFFFFF"), (18, "#D9F0F2"), (36, "#F8E8C8")]:
        parts.append(path(f"M {1468+offset} {338-offset*0.12:.1f} C {1502+offset} {322-offset*0.08:.1f}, {1540+offset} {322-offset*0.03:.1f}, {1578+offset} {338-offset*0.08:.1f}", stroke=color, stroke_width=4, extra='stroke-linecap="round" opacity="0.95"'))
    parts.append(text(1736, 308, "Reconstruct patient-specific fields", 20, fill=INK, weight=700, anchor="middle"))
    parts.append(text(1736, 348, "posterior mean, credible intervals,", 18, fill=MUTED, weight=500, anchor="middle"))
    parts.append(text(1736, 368, "and model-form uncertainty", 18, fill=MUTED, weight=500, anchor="middle"))

    parts.append(text(1402, 418, "Validation pathway", 22, fill=INK, weight=700))
    parts.append(line(1452, 462, 1814, 462, "#C9D6D6", stroke_width=4))
    for cx, accent, label1, label2 in [
        (1480, NAVY, "Synthetic", "known ground truth"),
        (1633, TEAL, "In vitro", "MRI / Echo / PIV-PTV"),
        (1786, RUST, "Clinical", "heart-disease cohorts"),
    ]:
        parts.append(circle(cx, 462, 28, fill="#FFFFFF", stroke=accent, stroke_width=4))
        parts.append(small_check(cx, 462, accent))
        parts.append(text(cx, 514, label1, 20, fill=INK, weight=700, anchor="middle"))
        parts.append(text(cx, 538, label2, 16, fill=MUTED, weight=500, anchor="middle"))

    parts.append(rect(1402, 548, 462, 78, fill="#F9F4EB", stroke="#E7D9BE", stroke_width=2, rx=24))
    parts.append(chip(1428, 566, 118, "Open-source", fill="#FFFFFF", text_fill=NAVY, stroke="#D9E1E3"))
    parts.append(chip(1558, 566, 128, "GPU-ready", fill="#FFFFFF", text_fill=TEAL, stroke="#D9E1E3"))
    parts.append(chip(1698, 566, 140, "Clinical UQ", fill="#FFFFFF", text_fill=RUST, stroke="#D9E1E3"))
    parts.append(text(1634, 612, "Improve medical image analysis, risk assessment, and clinical decisions.", 16, fill=INK, weight=600, anchor="middle"))

    parts.append(arrow_between(478, 526, 366, TEAL))
    parts.append(arrow_between(1344, 1392, 366, SKY))

    parts.append(text(54, 646, "Research plan: four specific aims", 26, fill=INK, weight=700))
    parts.append(text(54, 674, "Organized from formulation and representation to scalable inference and real-world demonstration.", 18, fill=MUTED, weight=500))
    parts.append(aim_card(54, 676, 447, 178, "1", ["Theoretical formulation"], ["priors for geometry, velocity, and pressure", "forward models for PC-MRI, 4D Flow, and Echo", "multimodal co-registration"], NAVY))
    parts.append(aim_card(519, 676, 447, 178, "2", ["Time-evolving", "parameterization"], ["spatial fields with explicit boundary conditions", "Markovian time evolution plus initial conditions", "convergence and sharp-feature resolution"], GOLD))
    parts.append(aim_card(984, 676, 447, 178, "3", ["Scalable posterior", "algorithms"], ["persistent / preconditioned SGLD", "amortized variational inference", "parallel Monte Carlo batching"], TEAL))
    parts.append(aim_card(1449, 676, 447, 178, "4", ["Verification to clinical", "demonstration"], ["synthetic data with analytical truth", "in vitro phantoms benchmarked by PIV/PTV", "clinical cohorts for model comparison"], RUST))

    parts.append("</svg>")
    return "\n".join(parts)


def export_png(svg_path: Path, png_path: Path) -> None:
    inkscape = shutil.which("inkscape")
    if inkscape is not None:
        try:
            subprocess.run(
                [
                    inkscape,
                    str(svg_path),
                    "--export-filename",
                    str(png_path),
                    "--export-width",
                    str(W),
                    "--export-height",
                    str(H),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        except (OSError, subprocess.CalledProcessError):
            pass

    rsvg = shutil.which("rsvg-convert")
    if rsvg is not None:
        subprocess.run(
            [
                rsvg,
                "--format",
                "png",
                "--output",
                str(png_path),
                "--width",
                str(W),
                "--height",
                str(H),
                str(svg_path),
            ],
            check=True,
        )
        return

    raise RuntimeError("No working SVG to PNG exporter found. Tried inkscape and rsvg-convert.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the NSF proposal master figure as SVG and PNG.")
    parser.add_argument("--svg", type=Path, required=True, help="Output SVG path.")
    parser.add_argument("--png", type=Path, required=True, help="Output PNG path.")
    args = parser.parse_args()

    args.svg.parent.mkdir(parents=True, exist_ok=True)
    args.png.parent.mkdir(parents=True, exist_ok=True)

    svg = build_svg()
    args.svg.write_text(svg + "\n", encoding="utf-8")
    export_png(args.svg, args.png)


if __name__ == "__main__":
    main()
