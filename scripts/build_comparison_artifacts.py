#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


RUNS_PARENT = Path("/tmp/worker-critic-example-runs")


@dataclass(frozen=True)
class ConditionSpec:
    slug: str
    title: str
    subtitle: str
    final_png_rel: str
    notes_rel: str


SPECS = (
    ConditionSpec(
        slug="base",
        title="A. Base",
        subtitle="No critic",
        final_png_rel="artifacts/master-figure/master-figure.png",
        notes_rel="artifacts/master-figure/notes.md",
    ),
    ConditionSpec(
        slug="critic",
        title="B. Same-Model Critic",
        subtitle="Persistent Codex worker + critic",
        final_png_rel="artifacts/master-figure-reviewed/master-figure.png",
        notes_rel="artifacts/master-figure-reviewed/notes.md",
    ),
    ConditionSpec(
        slug="external",
        title="C. External Pro Critic",
        subtitle="Persistent worker + gpt-5.4-pro reviewer",
        final_png_rel="artifacts/master-figure-external-review/master-figure.png",
        notes_rel="artifacts/master-figure-external-review/notes.md",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect finished benchmark runs and build comparison media."
    )
    parser.add_argument(
        "--run-prefix",
        required=True,
        help="Shared run prefix, e.g. 20260406-192417.",
    )
    parser.add_argument(
        "--runs-parent",
        type=Path,
        default=RUNS_PARENT,
        help="Parent directory containing the /tmp run workspaces.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Repo-local directory for copied finals and generated media.",
    )
    parser.add_argument(
        "--panel-width",
        type=int,
        default=1200,
        help="Width of each panel in the final side-by-side comparison.",
    )
    parser.add_argument(
        "--gif-width",
        type=int,
        default=1100,
        help="Width of each frame in the progress GIFs.",
    )
    return parser.parse_args()


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True)


def is_valid_image(path: Path) -> bool:
    result = subprocess.run(
        ["magick", "identify", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def resolve_run_root(runs_parent: Path, run_prefix: str, slug: str) -> Path:
    run_root = runs_parent / f"{run_prefix}-{slug}"
    if not run_root.exists():
        raise FileNotFoundError(f"Run root not found: {run_root}")
    return run_root


def run_records_dir(run_root: Path, run_prefix: str, slug: str) -> Path:
    run_id = f"{run_prefix}-{slug}"
    return run_root / "runs" / run_id


def copy_if_exists(source: Path, destination: Path) -> None:
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def build_panel(
    input_png: Path,
    output_png: Path,
    *,
    title: str,
    subtitle: str,
    panel_width: int,
) -> None:
    run_command(
        [
            "magick",
            str(input_png),
            "-resize",
            f"{panel_width}x",
            "-background",
            "#fbfcfe",
            "-gravity",
            "north",
            "-splice",
            "0x120",
            "-bordercolor",
            "#d9e0e8",
            "-border",
            "4x4",
            "-font",
            "Arial",
            "-fill",
            "#17324d",
            "-pointsize",
            "40",
            "-annotate",
            "+0+18",
            title,
            "-fill",
            "#5b6a78",
            "-pointsize",
            "24",
            "-annotate",
            "+0+72",
            subtitle,
            str(output_png),
        ]
    )


def build_side_by_side(
    panel_paths: list[Path],
    output_png: Path,
) -> None:
    run_command(["magick", *[str(path) for path in panel_paths], "+append", str(output_png)])


def build_labeled_frame(
    input_png: Path,
    output_png: Path,
    *,
    title: str,
    subtitle: str,
    frame_label: str,
    gif_width: int,
) -> None:
    run_command(
        [
            "magick",
            str(input_png),
            "-resize",
            f"{gif_width}x",
            "-background",
            "#fbfcfe",
            "-gravity",
            "north",
            "-splice",
            "0x132",
            "-bordercolor",
            "#d9e0e8",
            "-border",
            "4x4",
            "-font",
            "Arial",
            "-fill",
            "#17324d",
            "-pointsize",
            "34",
            "-annotate",
            "+0+14",
            title,
            "-fill",
            "#5b6a78",
            "-pointsize",
            "22",
            "-annotate",
            "+0+58",
            subtitle,
            "-fill",
            "#2d5a83",
            "-pointsize",
            "26",
            "-annotate",
            "+0+96",
            frame_label,
            str(output_png),
        ]
    )


def build_progress_gif(
    frame_paths: list[Path],
    output_gif: Path,
) -> None:
    if not frame_paths:
        raise ValueError("No frames provided for GIF build.")
    args = ["magick", "-delay", "110"]
    args.extend(str(path) for path in frame_paths[:-1])
    args.extend(["-delay", "220", str(frame_paths[-1]), "-loop", "0", "-layers", "Optimize", str(output_gif)])
    run_command(args)


def write_summary(summary_path: Path, lines: list[str]) -> None:
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()

    output_dir = args.output_dir
    copied_dir = output_dir / "finals"
    panels_dir = output_dir / "panels"
    gifs_dir = output_dir / "gifs"
    output_dir.mkdir(parents=True, exist_ok=True)
    copied_dir.mkdir(parents=True, exist_ok=True)
    panels_dir.mkdir(parents=True, exist_ok=True)
    gifs_dir.mkdir(parents=True, exist_ok=True)

    summary_lines = [
        f"# Comparison Artifacts for {args.run_prefix}",
        "",
        f"Runs parent: `{args.runs_parent}`",
        "",
        "Generated files:",
        f"- `final-comparison.png`: labeled final figures side by side.",
        f"- `gifs/*.gif`: labeled intermediate-draft progression for each condition.",
        "",
    ]

    panel_paths: list[Path] = []

    with TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        for spec in SPECS:
            run_root = resolve_run_root(args.runs_parent, args.run_prefix, spec.slug)
            run_records = run_records_dir(run_root, args.run_prefix, spec.slug)
            final_png = run_root / spec.final_png_rel
            notes_path = run_root / spec.notes_rel
            intermediate_dir = run_records / "intermediate"

            copied_png = copied_dir / f"{spec.slug}-final.png"
            copied_notes = copied_dir / f"{spec.slug}-notes.md"
            copy_if_exists(final_png, copied_png)
            copy_if_exists(notes_path, copied_notes)

            all_frame_paths = sorted(intermediate_dir.glob("*-master-figure.png"))
            frame_paths = [path for path in all_frame_paths if is_valid_image(path)]
            review_markdown = sorted((run_records / "reviews").glob("*.md"))

            panel_output = panels_dir / f"{spec.slug}-panel.png"
            build_panel(
                copied_png,
                panel_output,
                    title=spec.title,
                    subtitle=f"{spec.subtitle} | {len(frame_paths)} drafts | {len(review_markdown)} review files",
                    panel_width=args.panel_width,
                )
            panel_paths.append(panel_output)

            labeled_frames: list[Path] = []
            for index, frame_path in enumerate(frame_paths, start=1):
                frame_output = temp_dir / f"{spec.slug}-{index:04d}.png"
                build_labeled_frame(
                    frame_path,
                    frame_output,
                    title=spec.title,
                    subtitle=spec.subtitle,
                    frame_label=f"Draft {index} of {len(frame_paths)}",
                    gif_width=args.gif_width,
                )
                labeled_frames.append(frame_output)

            gif_output = gifs_dir / f"{spec.slug}-progress.gif"
            build_progress_gif(labeled_frames, gif_output)

            summary_lines.extend(
                [
                    f"## {spec.title}",
                    f"- Run root: `{run_root}`",
                    f"- Final PNG source: `{final_png}`",
                    f"- Notes source: `{notes_path}`",
                    f"- Intermediate PNG frames: `{len(frame_paths)}` valid of `{len(all_frame_paths)}` archived",
                    f"- Review markdown files: `{len(review_markdown)}`",
                    f"- Copied final PNG: `finals/{spec.slug}-final.png`",
                    f"- Progress GIF: `gifs/{spec.slug}-progress.gif`",
                    "",
                ]
            )

        build_side_by_side(panel_paths, output_dir / "final-comparison.png")
        write_summary(output_dir / "summary.md", summary_lines)


if __name__ == "__main__":
    main()
