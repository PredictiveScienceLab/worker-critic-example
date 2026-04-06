#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape


WIDTH = 1950
HEIGHT = 900

PALETTE = {
    "bg": "#F5F8FA",
    "ink": "#14324A",
    "muted": "#5A7184",
    "faint": "#90A3B2",
    "navy": "#153B5B",
    "blue": "#2C6EA4",
    "teal": "#2E7D78",
    "aqua": "#69AFC5",
    "gold": "#D7902E",
    "coral": "#C4634F",
    "sand": "#E9E2D4",
    "panel": "#FFFFFF",
    "line": "#D5E0E7",
    "chip_bg": "#EAF1F5",
}

SANS = "'Avenir Next', Avenir, 'Segoe UI', Helvetica, sans-serif"
SERIF = "Charter, 'Iowan Old Style', Georgia, serif"


def fmt(num: float) -> str:
    if abs(num - round(num)) < 1e-6:
        return str(int(round(num)))
    return f"{num:.2f}"


def wrap_text(text: str, width: float, font_size: float) -> list[str]:
    max_chars = max(1, int(width / (font_size * 0.57)))
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        lines.extend(
            textwrap.wrap(
                paragraph,
                width=max_chars,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return lines or [text]


def text_block(
    x: float,
    y: float,
    width: float,
    text: str,
    *,
    font_size: float,
    fill: str,
    family: str = SANS,
    weight: int | str = 500,
    line_height: float = 1.28,
    anchor: str = "start",
    opacity: float | None = None,
    letter_spacing: float | None = None,
) -> tuple[str, float]:
    lines = wrap_text(text, width, font_size)
    attrs = [
        f'x="{fmt(x if anchor == "start" else x + width / 2)}"',
        f'y="{fmt(y)}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'font-size="{fmt(font_size)}"',
        f'font-weight="{weight}"',
        'dominant-baseline="hanging"',
        f'text-anchor="{anchor}"',
    ]
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{fmt(letter_spacing)}"')
    dy = font_size * line_height
    parts = [f"<text {' '.join(attrs)}>"]
    for i, line in enumerate(lines):
        if i == 0:
            parts.append(f"<tspan>{escape(line)}</tspan>")
        else:
            if anchor == "start":
                parts.append(f'<tspan x="{fmt(x)}" dy="{fmt(dy)}">{escape(line)}</tspan>')
            else:
                parts.append(
                    f'<tspan x="{fmt(x + width / 2)}" dy="{fmt(dy)}">{escape(line)}</tspan>'
                )
    parts.append("</text>")
    height = font_size + max(0, len(lines) - 1) * dy
    return "".join(parts), height


def rounded_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    rx: float = 30,
    fill: str = PALETTE["panel"],
    stroke: str | None = None,
    stroke_width: float = 1,
    opacity: float | None = None,
    filter_id: str | None = "shadow",
) -> str:
    attrs = [
        f'x="{fmt(x)}"',
        f'y="{fmt(y)}"',
        f'width="{fmt(width)}"',
        f'height="{fmt(height)}"',
        f'rx="{fmt(rx)}"',
        f'fill="{fill}"',
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{fmt(stroke_width)}"')
    if opacity is not None:
        attrs.append(f'opacity="{fmt(opacity)}"')
    if filter_id:
        attrs.append(f'filter="url(#{filter_id})"')
    return f"<rect {' '.join(attrs)} />"


def pill(x: float, y: float, text: str, *, fill: str, stroke: str, text_fill: str) -> str:
    width = 30 + len(text) * 9.6
    rect = (
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="34" rx="17" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.2" />'
    )
    label = (
        f'<text x="{fmt(x + 14)}" y="{fmt(y + 8)}" fill="{text_fill}" font-family="{SANS}" '
        f'font-size="16" font-weight="700" dominant-baseline="hanging" text-anchor="start">'
        f"<tspan>{escape(text)}</tspan></text>"
    )
    return rect + label


def arrow(x1: float, y1: float, x2: float, y2: float, *, color: str, width: float = 6) -> str:
    return (
        f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
        f'stroke="{color}" stroke-width="{fmt(width)}" stroke-linecap="round" '
        f'marker-end="url(#arrowhead)" opacity="0.85" />'
    )


def modality_card(x: float, y: float, width: float, height: float, title: str, subtitle: str, kind: str) -> str:
    narrow = width < 220
    icon_size = height - 32
    icon_x = x + 16
    icon_y = y + 16
    cx = icon_x + icon_size / 2
    cy = icon_y + icon_size / 2
    title_x = icon_x + icon_size + 18
    title_y = y + 18
    title_size = 20 if narrow else (22 if height < 100 else 24)
    subtitle_size = 14.5 if narrow else (15.5 if height < 100 else 17)
    pieces = [
        rounded_rect(
            x,
            y,
            width,
            height,
            rx=26,
            fill="#FBFDFE",
            stroke=PALETTE["line"],
            stroke_width=1.3,
            filter_id=None,
        )
    ]
    pieces.append(
        f'<rect x="{fmt(icon_x)}" y="{fmt(icon_y)}" width="{fmt(icon_size)}" height="{fmt(icon_size)}" rx="18" '
        f'fill="#EFF6FA" stroke="{PALETTE["line"]}" stroke-width="1.2" />'
    )
    if kind == "pcmri":
        pieces.append(
            f'<rect x="{fmt(cx - 24)}" y="{fmt(cy - 18)}" width="48" height="36" rx="10" '
            f'fill="none" stroke="{PALETTE["blue"]}" stroke-width="3" />'
        )
        pieces.append(
            f'<circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="12" fill="none" stroke="{PALETTE["teal"]}" stroke-width="3" />'
        )
        pieces.append(
            f'<path d="M {fmt(cx - 20)} {fmt(cy + 24)} C {fmt(cx - 5)} {fmt(cy + 12)}, {fmt(cx + 5)} {fmt(cy + 36)}, {fmt(cx + 20)} {fmt(cy + 24)}" '
            f'fill="none" stroke="{PALETTE["gold"]}" stroke-width="3" stroke-linecap="round" />'
        )
    elif kind == "flow":
        pieces.append(
            f'<polygon points="{fmt(cx)} {fmt(cy - 24)} {fmt(cx + 24)} {fmt(cy - 8)} {fmt(cx + 24)} {fmt(cy + 20)} {fmt(cx)} {fmt(cy + 36)} {fmt(cx - 24)} {fmt(cy + 20)} {fmt(cx - 24)} {fmt(cy - 8)}" '
            f'fill="none" stroke="{PALETTE["blue"]}" stroke-width="3" />'
        )
        for shift in (-10, 6):
            pieces.append(
                f'<path d="M {fmt(cx - 12)} {fmt(cy + shift)} C {fmt(cx - 2)} {fmt(cy + shift - 8)}, {fmt(cx + 2)} {fmt(cy + shift + 8)}, {fmt(cx + 14)} {fmt(cy + shift)}" '
                f'fill="none" stroke="{PALETTE["teal"]}" stroke-width="3" stroke-linecap="round" marker-end="url(#miniArrow)" />'
            )
    else:
        pieces.append(
            f'<path d="M {fmt(cx - 30)} {fmt(cy + 28)} A 54 54 0 0 1 {fmt(cx + 30)} {fmt(cy + 28)}" '
            f'fill="none" stroke="{PALETTE["gold"]}" stroke-width="3" stroke-linecap="round" />'
        )
        for angle in (-24, -8, 8, 24):
            x2 = cx + 34 * math.sin(math.radians(angle))
            y2 = cy + 28 - 34 * math.cos(math.radians(angle))
            pieces.append(
                f'<line x1="{fmt(cx)}" y1="{fmt(cy + 28)}" x2="{fmt(x2)}" y2="{fmt(y2)}" '
                f'stroke="{PALETTE["coral"]}" stroke-width="2.8" stroke-linecap="round" />'
            )
        pieces.append(
            f'<path d="M {fmt(cx - 10)} {fmt(cy + 8)} C {fmt(cx - 8)} {fmt(cy - 12)}, {fmt(cx + 10)} {fmt(cy - 10)}, {fmt(cx + 12)} {fmt(cy + 8)}" '
            f'fill="none" stroke="{PALETTE["teal"]}" stroke-width="3" stroke-linecap="round" />'
        )
    title_svg, _ = text_block(
        title_x,
        title_y,
        width - (title_x - x) - 16,
        title,
        font_size=title_size,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
    )
    subtitle_svg, _ = text_block(
        title_x,
        y + 48,
        width - (title_x - x) - 16,
        subtitle,
        font_size=subtitle_size,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.32,
    )
    pieces.append(title_svg)
    pieces.append(subtitle_svg)
    return "".join(pieces)


def numbered_aim_card(
    x: float,
    y: float,
    width: float,
    height: float,
    number: int,
    title: str,
    body: str,
    color: str,
) -> str:
    pieces = [
        rounded_rect(
            x,
            y,
            width,
            height,
            rx=28,
            fill="#FFFFFF",
            stroke="#D8E3EA",
            stroke_width=1.3,
            filter_id="shadow",
        ),
        f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(width)}" height="12" rx="12" fill="{color}" />',
        f'<circle cx="{fmt(x + 52)}" cy="{fmt(y + 48)}" r="27" fill="{color}" />',
    ]
    pieces.append(
        f'<text x="{fmt(x + 52)}" y="{fmt(y + 38)}" fill="#FFFFFF" font-family="{SANS}" '
        f'font-size="28" font-weight="800">{number}</text>'
    )
    title_svg, _ = text_block(
        x + 94,
        y + 24,
        width - 118,
        title,
        font_size=24,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
    )
    body_svg, _ = text_block(
        x + 28,
        y + 88,
        width - 56,
        body,
        font_size=18,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.35,
    )
    pieces.extend([title_svg, body_svg])
    return "".join(pieces)


def verification_step(
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    body: str,
    color: str,
) -> str:
    pieces = [
        rounded_rect(
            x,
            y,
            width,
            height,
            rx=22,
            fill="#FCFDFE",
            stroke="#D8E3EA",
            stroke_width=1.2,
            filter_id=None,
        ),
        f'<rect x="{fmt(x + 16)}" y="{fmt(y + 12)}" width="10" height="{fmt(height - 24)}" rx="5" fill="{color}" />',
    ]
    title_svg, _ = text_block(
        x + 46,
        y + 12,
        width - 64,
        title,
        font_size=18.5,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
    )
    body_svg, _ = text_block(
        x + 46,
        y + 34,
        width - 64,
        body,
        font_size=14.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
    )
    pieces.extend([title_svg, body_svg])
    return "".join(pieces)


def build_svg() -> str:
    out: list[str] = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">'
    )
    out.append("<title id=\"title\">Overview of the NSF cardiovascular hemodynamics proposal</title>")
    out.append(
        "<desc id=\"desc\">One-glance overview showing multimodal imaging inputs, the information field theory engine, four specific aims, validation path, and expected impact.</desc>"
    )
    out.append(
        """
<defs>
  <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#F7FAFB"/>
    <stop offset="55%" stop-color="#F3F7FA"/>
    <stop offset="100%" stop-color="#FCF8F2"/>
  </linearGradient>
  <linearGradient id="bannerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stop-color="#163B5A"/>
    <stop offset="100%" stop-color="#245E7F"/>
  </linearGradient>
  <linearGradient id="engineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#F8FBFD"/>
    <stop offset="100%" stop-color="#EEF5F8"/>
  </linearGradient>
  <linearGradient id="impactGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#FFFDFC"/>
    <stop offset="100%" stop-color="#F8F3EA"/>
  </linearGradient>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="160%">
    <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0E2236" flood-opacity="0.08"/>
  </filter>
  <marker id="arrowhead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="#5F7D94"/>
  </marker>
  <marker id="miniArrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
    <path d="M 0 0 L 8 4 L 0 8 z" fill="#2E7D78"/>
  </marker>
</defs>
"""
    )
    out.append(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#bgGrad)" />')
    out.append('<circle cx="218" cy="128" r="202" fill="#E6F1F3" opacity="0.65" />')
    out.append('<circle cx="1768" cy="114" r="178" fill="#F3EBDD" opacity="0.55" />')
    out.append('<circle cx="1650" cy="786" r="220" fill="#EAF2F7" opacity="0.55" />')
    out.append(
        '<path d="M 70 630 C 360 540, 540 700, 760 612 S 1180 520, 1510 610 S 1750 664, 1886 594" '
        'fill="none" stroke="#D9EAF0" stroke-width="18" stroke-linecap="round" opacity="0.55" />'
    )

    out.append(rounded_rect(56, 42, 1838, 154, rx=38, fill="#FFFFFF", stroke="#D9E4EB", stroke_width=1.2))
    out.append(
        f'<rect x="76" y="62" width="12" height="114" rx="6" fill="{PALETTE["gold"]}" />'
    )
    kicker, _ = text_block(
        106,
        66,
        560,
        "Proposal at a glance",
        font_size=20,
        fill=PALETTE["blue"],
        family=SANS,
        weight=800,
        letter_spacing=0.8,
    )
    title, _ = text_block(
        106,
        96,
        1120,
        "Information field theory for hemodynamic imaging",
        font_size=38,
        fill=PALETTE["ink"],
        family=SERIF,
        weight=700,
        line_height=1.1,
    )
    subtitle, _ = text_block(
        106,
        146,
        1120,
        "Fuse noisy PC-MRI, 4D Flow MRI, and Doppler Echo with physics-informed Bayesian inference to recover geometry, flow, pressure, and uncertainty.",
        font_size=21,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.32,
    )
    out.extend([kicker, title, subtitle])

    out.append(
        rounded_rect(
            1314,
            60,
            548,
            118,
            rx=28,
            fill="url(#bannerGrad)",
            stroke=None,
            filter_id=None,
        )
    )
    objective_label, _ = text_block(
        1346,
        82,
        484,
        "Central objective",
        font_size=19,
        fill="#CFE3F3",
        family=SANS,
        weight=800,
        letter_spacing=0.7,
    )
    objective_text, _ = text_block(
        1346,
        110,
        484,
        "Scalable Bayesian reconstruction of cardiovascular hemodynamic fields and cardiac structure from advanced imaging.",
        font_size=19,
        fill="#FFFFFF",
        family=SANS,
        weight=700,
        line_height=1.22,
    )
    out.extend([objective_label, objective_text])

    out.append(rounded_rect(56, 222, 440, 442, rx=34, fill="#FFFFFF", stroke="#D8E3EA", stroke_width=1.2))
    left_label, _ = text_block(
        88,
        252,
        320,
        "Inputs + inverse-problem challenge",
        font_size=28,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
        line_height=1.16,
    )
    left_note, _ = text_block(
        88,
        318,
        360,
        "Velocity data are informative but still noisy, partial, and patient specific.",
        font_size=17.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.34,
    )
    out.extend([left_label, left_note])
    out.append(pill(88, 388, "noisy", fill="#EEF4FB", stroke="#C7DAEC", text_fill=PALETTE["blue"]))
    out.append(pill(172, 388, "partial", fill="#EEF7F5", stroke="#B9DDD8", text_fill=PALETTE["teal"]))
    out.append(pill(270, 388, "misregistered", fill="#FBF2E5", stroke="#E9D1A7", text_fill=PALETTE["gold"]))
    out.append(pill(88, 426, "unknown BCs", fill="#F9EFEB", stroke="#E5C5BC", text_fill=PALETTE["coral"]))
    out.append(pill(230, 426, "patient parameters", fill="#EAF1F5", stroke="#C7D5E0", text_fill=PALETTE["ink"]))
    out.append(modality_card(88, 470, 180, 82, "PC-MRI", "Phase-contrast data", "pcmri"))
    out.append(modality_card(284, 470, 180, 82, "4D Flow", "Time-resolved MRI", "flow"))
    out.append(modality_card(88, 570, 376, 82, "Doppler Echo", "Ultrasound line-of-sight flow", "echo"))

    out.append(rounded_rect(520, 222, 896, 442, rx=34, fill="url(#engineGrad)", stroke="#D8E3EA", stroke_width=1.2))
    engine_label, _ = text_block(
        552,
        252,
        340,
        "Information Field Theory engine",
        font_size=29,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
    )
    engine_note, _ = text_block(
        552,
        292,
        824,
        "Bayesian inference over fields fuses measurements and known physics without repeatedly calling a CFD solver.",
        font_size=18.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.3,
    )
    out.extend([engine_label, engine_note])

    out.append(rounded_rect(552, 344, 256, 192, rx=26, fill="#FFFFFF", stroke="#D9E4EB", stroke_width=1.2, filter_id=None))
    prior_title, _ = text_block(
        576,
        368,
        206,
        "Physics-informed prior",
        font_size=24,
        fill=PALETTE["teal"],
        family=SANS,
        weight=800,
    )
    prior_body, _ = text_block(
        576,
        406,
        206,
        "Eikonal, continuity, and Navier-Stokes priors encode geometry, flow, pressure, and model error.",
        font_size=16.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.34,
    )
    out.extend([prior_title, prior_body])

    out.append(rounded_rect(1128, 344, 256, 192, rx=26, fill="#FFFFFF", stroke="#D9E4EB", stroke_width=1.2, filter_id=None))
    meas_title, _ = text_block(
        1152,
        368,
        208,
        "Data Hamiltonian",
        font_size=24,
        fill=PALETTE["blue"],
        family=SANS,
        weight=800,
    )
    meas_body, _ = text_block(
        1152,
        406,
        208,
        "Modality-specific operators and co-registration connect latent fields to PC-MRI, 4D Flow, and Echo data.",
        font_size=16.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.34,
    )
    out.extend([meas_title, meas_body])

    out.append(
        rounded_rect(
            838,
            330,
            290,
            220,
            rx=34,
            fill=PALETTE["navy"],
            stroke=None,
            filter_id="shadow",
        )
    )
    formula_label, _ = text_block(
        864,
        352,
        238,
        "Joint posterior",
        font_size=19,
        fill="#CFE3F3",
        family=SANS,
        weight=800,
        anchor="middle",
    )
    formula_main, _ = text_block(
        852,
        392,
        262,
        "data + physics -> posterior",
        font_size=24,
        fill="#FFFFFF",
        family=SERIF,
        weight=700,
        anchor="middle",
        line_height=1.18,
    )
    formula_sub, _ = text_block(
        866,
        458,
        234,
        "Infer geometry g(x,t), velocity v(x,t), pressure tau(x,t), wall motion, and hyperparameters.",
        font_size=16,
        fill="#D7E7F4",
        family=SANS,
        weight=500,
        anchor="middle",
        line_height=1.32,
    )
    out.extend([formula_label, formula_main, formula_sub])
    out.append(arrow(808, 440, 838, 440, color="#5F7D94"))
    out.append(arrow(1128, 440, 1120, 440, color="#5F7D94"))

    out.append(pill(570, 552, "No repeated CFD solver", fill="#EEF7F5", stroke="#B9DDD8", text_fill=PALETTE["teal"]))
    out.append(pill(790, 552, "Fuses modalities", fill="#EEF4FB", stroke="#C7DAEC", text_fill=PALETTE["blue"]))
    out.append(pill(986, 552, "Quantifies uncertainty", fill="#FBF2E5", stroke="#E9D1A7", text_fill=PALETTE["gold"]))
    out.append(pill(1194, 552, "GPU-scale inference", fill="#F1EEF8", stroke="#D6CCE8", text_fill=PALETTE["navy"]))

    out.append(rounded_rect(1440, 222, 454, 442, rx=34, fill="url(#impactGrad)", stroke="#D8E3EA", stroke_width=1.2))
    right_label, _ = text_block(
        1472,
        252,
        362,
        "Validation ladder + expected outcomes",
        font_size=28,
        fill=PALETTE["ink"],
        family=SANS,
        weight=800,
        line_height=1.16,
    )
    right_note, _ = text_block(
        1472,
        324,
        362,
        "Synthetic truth to in vitro phantoms to clinical cohorts.",
        font_size=17,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.34,
    )
    out.extend([right_label, right_note])
    out.append(verification_step(1472, 368, 390, 68, "1. Synthetic verification", "Known truth, noise studies, convergence checks.", PALETTE["blue"]))
    out.append(verification_step(1472, 446, 390, 68, "2. In vitro validation", "Cross-modality phantoms benchmarked with PIV/PTV.", PALETTE["teal"]))
    out.append(verification_step(1472, 524, 390, 68, "3. Clinical demonstration", "Mouse, RV, aortic, and congenital-heart cohorts.", PALETTE["coral"]))
    out.append(
        rounded_rect(
            1472,
            602,
            390,
            60,
            rx=24,
            fill="#FFFFFF",
            stroke="#D8E3EA",
            stroke_width=1.2,
            filter_id="shadow",
        )
    )
    impact_body, _ = text_block(
        1498,
        604,
        334,
        "Posterior fields with uncertainty, imaging guidance, open-source GPU tools, and benchmark data.",
        font_size=15.5,
        fill=PALETTE["muted"],
        family=SANS,
        weight=500,
        line_height=1.34,
    )
    out.append(impact_body)

    out.append(arrow(496, 434, 520, 434, color="#7D96A9"))
    out.append(arrow(1416, 434, 1440, 434, color="#7D96A9"))

    aims_label, _ = text_block(
        72,
        682,
        220,
        "Specific aims",
        font_size=21,
        fill=PALETTE["blue"],
        family=SANS,
        weight=800,
        letter_spacing=0.7,
    )
    out.append(aims_label)
    out.append(numbered_aim_card(56, 718, 444, 158, 1, "Formulate the inverse problem", "Physics-informed priors, measurement operators, and co-registration.", PALETTE["blue"]))
    out.append(numbered_aim_card(518, 718, 444, 158, 2, "Parameterize spatiotemporal fields", "Spatial bases and dynamics-aware time evolution.", PALETTE["teal"]))
    out.append(numbered_aim_card(980, 718, 444, 158, 3, "Scale posterior inference", "Advanced SGLD, amortized VI, and distributed batches.", PALETTE["gold"]))
    out.append(numbered_aim_card(1442, 718, 452, 158, 4, "Verify, validate, demonstrate", "Synthetic truth, in vitro phantoms, and clinical cohorts.", PALETTE["coral"]))

    out.append("</svg>")
    return "".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the master proposal figure as SVG.")
    parser.add_argument("--output", required=True, help="Output SVG path")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()
