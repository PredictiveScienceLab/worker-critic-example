from __future__ import annotations

import argparse
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape


WIDTH = 1950
HEIGHT = 900


def wrap_lines(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            lines.append("")
            continue
        lines.extend(textwrap.wrap(paragraph, width=width, break_long_words=False))
    return lines


def tspan_block(
    x: float,
    y: float,
    text: str,
    *,
    size: int = 18,
    weight: int = 400,
    fill: str = "#19323c",
    width: int | None = None,
    line_gap: float = 1.28,
    anchor: str = "start",
    family: str = "Avenir Next, Avenir, Helvetica Neue, Arial, sans-serif",
    letter_spacing: float | None = None,
) -> str:
    lines = wrap_lines(text, width) if width else text.split("\n")
    attrs = [
        f'x="{x}"',
        f'y="{y}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'text-anchor="{anchor}"',
    ]
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing}"')
    parts = [f"<text {' '.join(attrs)}>"]
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else size * line_gap
        parts.append(f'<tspan x="{x}" dy="{dy}">{escape(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def rounded_panel(
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: str,
    stroke: str = "#d8ddd9",
    radius: int = 28,
    shadow: bool = False,
    stroke_width: int = 1,
) -> str:
    filter_attr = ' filter="url(#shadow)"' if shadow else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"'
        f' fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{filter_attr}/>'
    )


def chip(x: float, y: float, w: float, h: float, text: str, fill: str, text_fill: str) -> str:
    return (
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{fill}"/>'
        + tspan_block(x + w / 2, y + h / 2 + 6, text, size=15, weight=700, fill=text_fill, anchor="middle")
        + "</g>"
    )


def bullet_list(
    x: float,
    y: float,
    items: list[str],
    *,
    width: int,
    size: int = 18,
    fill: str = "#2c3f46",
    bullet_fill: str = "#2d6f75",
    row_gap: float = 1.25,
) -> str:
    parts = ["<g>"]
    cursor_y = y
    for item in items:
        lines = wrap_lines(item, width)
        parts.append(f'<circle cx="{x}" cy="{cursor_y - size * 0.35}" r="4.5" fill="{bullet_fill}"/>')
        parts.append(tspan_block(x + 14, cursor_y, "\n".join(lines), size=size, fill=fill, width=None))
        cursor_y += size * row_gap * max(1, len(lines)) + 8
    parts.append("</g>")
    return "".join(parts)


def arrow(x1: float, y1: float, x2: float, y2: float, color: str = "#6f8f92", width: int = 4) -> str:
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{width}" stroke-linecap="round" marker-end="url(#arrow)"/>'
    )


def icon_mri(x: float, y: float, scale: float = 1.0) -> str:
    return f"""
    <g transform="translate({x},{y}) scale({scale})">
      <rect x="6" y="20" width="88" height="58" rx="18" fill="#f6fbfb" stroke="#2d6f75" stroke-width="4"/>
      <circle cx="50" cy="49" r="16" fill="none" stroke="#2d6f75" stroke-width="6"/>
      <rect x="52" y="44" width="46" height="10" rx="5" fill="#2d6f75" opacity="0.22"/>
      <rect x="84" y="39" width="28" height="20" rx="10" fill="#2d6f75"/>
    </g>
    """


def icon_flow(x: float, y: float, scale: float = 1.0) -> str:
    return f"""
    <g transform="translate({x},{y}) scale({scale})">
      <polygon points="16,62 48,44 81,58 49,76" fill="#f6f2e6" stroke="#b48a1e" stroke-width="4"/>
      <polygon points="16,62 16,24 48,8 48,44" fill="#fcf8ef" stroke="#b48a1e" stroke-width="4"/>
      <polygon points="48,44 48,8 81,22 81,58" fill="#f6ecd0" stroke="#b48a1e" stroke-width="4"/>
      <path d="M26 52 C36 46, 44 46, 56 34" fill="none" stroke="#b48a1e" stroke-width="5" marker-end="url(#arrowGold)"/>
      <path d="M39 62 C47 56, 56 54, 69 42" fill="none" stroke="#b48a1e" stroke-width="5" marker-end="url(#arrowGold)"/>
    </g>
    """


def icon_echo(x: float, y: float, scale: float = 1.0) -> str:
    return f"""
    <g transform="translate({x},{y}) scale({scale})">
      <path d="M20 18 L52 8 L70 28 L36 38 Z" fill="#d77a61" opacity="0.22" stroke="#c15d43" stroke-width="4"/>
      <rect x="52" y="8" width="18" height="48" rx="9" fill="#c15d43"/>
      <path d="M20 42 Q52 68 84 42" fill="none" stroke="#c15d43" stroke-width="4"/>
      <path d="M24 42 Q52 60 80 42" fill="none" stroke="#c15d43" stroke-width="3"/>
      <path d="M28 42 Q52 52 76 42" fill="none" stroke="#c15d43" stroke-width="2.5"/>
      <path d="M12 62 C30 54, 48 54, 74 72" fill="none" stroke="#c15d43" stroke-width="5" marker-end="url(#arrowCoral)"/>
    </g>
    """


def vessel_graphic(x: float, y: float, scale: float = 1.0) -> str:
    return f"""
    <g transform="translate({x},{y}) scale({scale})">
      <path d="M18 80 C45 28, 104 28, 134 56 C162 82, 213 85, 246 46"
            fill="none" stroke="#cfe6ea" stroke-width="36" stroke-linecap="round"/>
      <path d="M18 80 C45 28, 104 28, 134 56 C162 82, 213 85, 246 46"
            fill="none" stroke="#2d6f75" stroke-width="12" stroke-linecap="round"/>
      <path d="M27 78 C60 36, 101 38, 126 55" fill="none" stroke="#f7f6f2" stroke-width="6" opacity="0.9"/>
      <path d="M140 60 C170 80, 206 79, 236 52" fill="none" stroke="#f7f6f2" stroke-width="6" opacity="0.9"/>
      <path d="M34 79 C56 49, 84 43, 113 48" fill="none" stroke="#c15d43" stroke-width="5" marker-end="url(#arrowCoral)"/>
      <path d="M138 61 C165 76, 191 74, 224 55" fill="none" stroke="#c15d43" stroke-width="5" marker-end="url(#arrowCoral)"/>
      <circle cx="111" cy="48" r="8" fill="#b48a1e"/>
      <circle cx="179" cy="74" r="7" fill="#b48a1e"/>
    </g>
    """


def validation_step(x: float, y: float, w: float, h: float, title: str, text: str, fill: str, accent: str) -> str:
    parts = [
        f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" stroke="{accent}" stroke-width="1.5"/>',
        tspan_block(x + 22, y + 34, title, size=21, weight=800, fill="#163038"),
        tspan_block(x + 22, y + 68, text, size=17, fill="#39525b", width=18),
        "</g>",
    ]
    return "".join(parts)


def aim_card(x: float, y: float, w: float, h: float, number: int, title: str, items: list[str], accent: str, tint: str) -> str:
    parts = [
        f'<g>{rounded_panel(x, y, w, h, fill="#ffffff", stroke="#d9dfdb", radius=26)}',
        f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="26" fill="{accent}"/>',
        f'<circle cx="{x + 42}" cy="{y + 52}" r="21" fill="{tint}" stroke="{accent}" stroke-width="2"/>',
        tspan_block(x + 42, y + 60, str(number), size=22, weight=800, fill=accent, anchor="middle"),
        tspan_block(x + 75, y + 40, f"Specific Aim {number}", size=16, weight=800, fill="#6a7d84", letter_spacing=1.4),
        tspan_block(x + 75, y + 70, title, size=24, weight=800, fill="#17323a", width=24),
        bullet_list(x + 28, y + 122, items, width=30, size=18, bullet_fill=accent),
        "</g>",
    ]
    return "".join(parts)


def build_svg() -> str:
    s: list[str] = []
    s.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
    )
    s.append(
        """
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#6f8f92"/>
          </marker>
          <marker id="arrowGold" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#b48a1e"/>
          </marker>
          <marker id="arrowCoral" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#c15d43"/>
          </marker>
        </defs>
        """
    )
    s.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="#f7f6f2"/>')

    # Header.
    s.append(rounded_panel(60, 40, 1830, 108, fill="#ffffff", stroke="#d9dfdb", radius=30))
    s.append(tspan_block(96, 94, "Information Field Theory for Uncertainty-Aware Cardiovascular Reconstruction", size=40, weight=850, fill="#17323a", width=80))
    s.append(
        tspan_block(
            96,
            132,
            "Objective: reconstruct cardiac structure and hemodynamic fields from advanced medical imaging with quantified uncertainty.",
            size=20,
            fill="#466068",
            width=100,
        )
    )

    # Main connectors.
    s.append(arrow(603, 350, 625, 350, color="#95afb1", width=4))
    s.append(arrow(1335, 350, 1354, 350, color="#95afb1", width=4))

    # Left panel.
    left_x, top_y, left_w, panel_h = 60, 175, 540, 355
    s.append(rounded_panel(left_x, top_y, left_w, panel_h, fill="#ffffff", stroke="#dce3df", radius=30))
    s.append(tspan_block(left_x + 30, top_y + 38, "Clinical challenge and data", size=16, weight=800, fill="#6b7f85", letter_spacing=1.6))
    s.append(tspan_block(left_x + 30, top_y + 78, "Advanced imaging is informative but incomplete.", size=29, weight=850, fill="#17323a", width=28))
    card_y = top_y + 198
    card_w = 150
    gap = 16
    card_specs = [
        ("PC-MRI", "#edf6f7", "#2d6f75"),
        ("4D Flow MRI", "#faf5e8", "#b48a1e"),
        ("Doppler Echo", "#fbefeb", "#c15d43"),
    ]
    for i, (title, tint, accent) in enumerate(card_specs):
        x = left_x + 28 + i * (card_w + gap)
        s.append(f'<rect x="{x}" y="{card_y}" width="{card_w}" height="118" rx="22" fill="{tint}" stroke="{accent}" stroke-opacity="0.35"/>')
        if i == 0:
            s.append(icon_mri(x + 18, card_y + 16, 0.95))
        elif i == 1:
            s.append(icon_flow(x + 24, card_y + 14, 0.92))
        else:
            s.append(icon_echo(x + 24, card_y + 16, 0.92))
        s.append(tspan_block(x + 16, card_y + 98, title, size=20, weight=800, fill="#17323a", width=13))
    # Center panel.
    cx, cw = 630, 700
    s.append(rounded_panel(cx, top_y, cw, panel_h, fill="#ffffff", stroke="#d7e4e6", radius=30))
    s.append(tspan_block(cx + 30, top_y + 38, "Information Field Theory engine", size=16, weight=800, fill="#6b7f85", letter_spacing=1.6))
    s.append(
        tspan_block(
            cx + 30,
            top_y + 76,
            "Fuse physical laws and multimodal imaging in a Bayesian inverse problem over fields.",
            size=27,
            weight=850,
            fill="#17323a",
            width=45,
        )
    )
    small_y = top_y + 136
    small_specs = [
        (
            cx + 26,
            "Physics-informed priors",
            "Eikonal, continuity,\nNavier-Stokes",
            "#edf6f7",
            "#2d6f75",
        ),
        (
            cx + 252,
            "Measurement operators",
            "MRI / Echo likelihoods\n+ co-registration",
            "#faf5e8",
            "#b48a1e",
        ),
        (
            cx + 478,
            "Representation and inference",
            "spatial dynamics,\nSGLD, amortized VI",
            "#fbefeb",
            "#c15d43",
        ),
    ]
    for x, title, detail, fill, accent in small_specs:
        s.append(f'<rect x="{x}" y="{small_y}" width="196" height="116" rx="22" fill="{fill}" stroke="{accent}" stroke-opacity="0.35"/>')
        s.append(tspan_block(x + 18, small_y + 32, title, size=18, weight=800, fill="#17323a", width=18))
        s.append(tspan_block(x + 18, small_y + 70, detail, size=17, fill="#4a6269", width=18))
        s.append(arrow(x + 98, small_y + 116, cx + 350, top_y + 252, color=accent, width=2))

    posterior_x, posterior_y = cx + 100, top_y + 240
    s.append(f'<rect x="{posterior_x}" y="{posterior_y}" width="500" height="100" rx="26" fill="#153a43" stroke="#0f2d34" filter="url(#shadow)"/>')
    s.append(vessel_graphic(posterior_x + 10, posterior_y + 12, 0.70))
    s.append(tspan_block(posterior_x + 205, posterior_y + 40, "Posterior over fields\n+ parameters", size=21, weight=850, fill="#f6fbfb"))

    # Right panel.
    rx, rw = 1360, 530
    s.append(rounded_panel(rx, top_y, rw, panel_h, fill="#ffffff", stroke="#dde4df", radius=30))
    s.append(tspan_block(rx + 30, top_y + 38, "Validated outputs and impact", size=16, weight=800, fill="#6b7f85", letter_spacing=1.6))
    s.append(
        tspan_block(
            rx + 30,
            top_y + 76,
            "Recover posterior cardiovascular fields with quantified uncertainty.",
            size=26,
            weight=850,
            fill="#17323a",
            width=30,
        )
    )
    s.append(f'<rect x="{rx + 28}" y="{top_y + 156}" width="474" height="102" rx="24" fill="#eef6f7" stroke="#2d6f75" stroke-opacity="0.28"/>')
    s.append(vessel_graphic(rx + 34, top_y + 166, 0.72))
    s.append(
        bullet_list(
            rx + 220,
            top_y + 186,
            [
                "geometry, velocity, pressure, and uncertainty",
                "biomarkers, decisions, and open tools",
            ],
            width=25,
            size=18,
            bullet_fill="#2d6f75",
        )
    )
    s.append(tspan_block(rx + 30, top_y + 286, "Trust-building path", size=18, weight=800, fill="#17323a"))
    s.append(validation_step(rx + 28, top_y + 306, 136, 54, "Synthetic", "known truth", "#f8fbfb", "#2d6f75"))
    s.append(validation_step(rx + 196, top_y + 306, 136, 54, "In vitro", "phantoms + PIV/PTV", "#fefaf2", "#b48a1e"))
    s.append(validation_step(rx + 364, top_y + 306, 138, 54, "Clinical", "retrospective data", "#fdf3f0", "#c15d43"))
    s.append(arrow(rx + 164, top_y + 333, rx + 194, top_y + 333, color="#95afb1", width=3))
    s.append(arrow(rx + 332, top_y + 333, rx + 362, top_y + 333, color="#95afb1", width=3))

    # Bottom row.
    s.append(tspan_block(60, 566, "Four specific aims", size=17, weight=800, fill="#6b7f85", letter_spacing=1.8))
    aim_y, aim_h, aim_w = 586, 240, 435
    aim_gap = 20
    aim_specs = [
        (
            1,
            "Formulate the inverse problem",
            [
                "priors for moving geometry and flow",
                "MRI / Echo operators and Bayesian co-registration",
            ],
            "#2d6f75",
            "#e5f1f2",
        ),
        (
            2,
            "Parameterize time-evolving fields",
            [
                "boundary-aware spatial bases",
                "dynamic parameterization of time evolution",
            ],
            "#7c9d88",
            "#ebf3ed",
        ),
        (
            3,
            "Scale posterior inference",
            [
                "persistent / preconditioned SGLD",
                "amortized VI for batched GPU inference",
            ],
            "#c15d43",
            "#faece8",
        ),
        (
            4,
            "Verify, validate, and demonstrate",
            [
                "synthetic and in vitro validation",
                "clinical demonstration on retrospective data",
            ],
            "#b48a1e",
            "#faf2de",
        ),
    ]
    for i, spec in enumerate(aim_specs):
        x = 60 + i * (aim_w + aim_gap)
        s.append(aim_card(x, aim_y, aim_w, aim_h, *spec))

    s.append("</svg>")
    return "".join(s)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(build_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()
