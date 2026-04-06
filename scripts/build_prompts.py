from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO_ROOT / "prompts"


@dataclass(frozen=True)
class PromptVariant:
    output_path: Path
    addendum_paths: tuple[Path, ...]


BASE_PROMPT = PROMPTS_DIR / "generate-master-figure.md"

VARIANTS = {
    "with_critic": PromptVariant(
        output_path=PROMPTS_DIR / "generate-master-figure-with-critic.md",
        addendum_paths=(PROMPTS_DIR / "critic-review-addendum.md",),
    ),
}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def build_prompt(base_path: Path, addendum_paths: tuple[Path, ...]) -> str:
    sections = [load_text(base_path), *(load_text(path) for path in addendum_paths)]
    return "\n\n".join(sections) + "\n"


def write_prompt(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def main() -> None:
    base_text = load_text(BASE_PROMPT)

    for variant in VARIANTS.values():
        merged = build_prompt(BASE_PROMPT, variant.addendum_paths)
        if not merged.startswith(base_text):
            raise ValueError(f"Generated prompt at {variant.output_path} does not preserve the base prompt verbatim.")
        write_prompt(variant.output_path, merged)
        print(f"Wrote {variant.output_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
