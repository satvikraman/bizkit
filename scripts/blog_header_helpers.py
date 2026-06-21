#!/usr/bin/env python3
"""Helpers for blog header image generation workflow."""
import argparse
import re
import subprocess
import sys
from pathlib import Path

PREFIX = (
    "Please generate a vibrant image for the blog post below. "
    "Get the context by scanning the contents of the blog post. "
    "The image should visually represent the concept being discussed in the post. "
    "Use graphic elements to explain the concept. "
    "The style should be modern and appealing to high school students, "
    "with bright colors and clear imagery. "
    "Ensure the image is suitable for use as a blog post header since it "
    "will eventually be scaled to 664x548. "
    "IMPORTANT: Do not depict any real politicians, celebrities, or identifiable "
    "public figures. Use only abstract icons, symbols, charts, and graphic elements. "
)

REPO = Path(__file__).resolve().parent.parent
VENV_PYTHON = REPO / ".venv" / "bin" / "python"
RESIZE_SCRIPT = REPO / "scripts" / "resize_image.py"
DOWNLOADS = Path.home() / "Downloads"
PAGEVIEWS_RE = re.compile(r"<p><b>Pageviews:</b>", re.IGNORECASE)


def get_body(qmd_path: Path) -> str:
    text = qmd_path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    body = parts[2].strip() if len(parts) >= 3 else text.strip()
    lines = [line for line in body.splitlines() if not PAGEVIEWS_RE.search(line)]
    return " ".join(" ".join(lines).split())


def build_prompt(folder: str) -> str:
    qmd = REPO / "blog" / folder / "index-en.qmd"
    if not qmd.exists():
        raise FileNotFoundError(f"Missing {qmd}")
    return PREFIX + get_body(qmd)


def copy_prompt(folder: str) -> Path:
    prompt = build_prompt(folder)
    out = Path("/tmp") / f"blog_prompt_{folder}.txt"
    out.write_text(prompt, encoding="utf-8")
    subprocess.run(["pbcopy"], input=prompt.encode("utf-8"), check=True)
    return out


def newest_gemini_download(before_names: set[str] | None = None) -> Path | None:
    files = sorted(
        DOWNLOADS.glob("Gemini_Generated_Image*.png"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for f in files:
        if before_names is None or f.name not in before_names:
            return f
    return files[0] if files else None


def list_gemini_downloads() -> set[str]:
    return {p.name for p in DOWNLOADS.glob("Gemini_Generated_Image*.png")}


def finalize(folder: str, before: set[str] | None = None) -> tuple[bool, str]:
    src = newest_gemini_download(before)
    if src is None:
        return False, "No Gemini_Generated_Image*.png found in ~/Downloads"
    dest = REPO / "blog" / folder / f"title_{folder}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dest)
    subprocess.run([str(VENV_PYTHON), str(RESIZE_SCRIPT), str(dest.parent)], check=True)
    from PIL import Image

    with Image.open(dest) as img:
        if img.size != (664, 548):
            return False, f"Wrong size after resize: {img.size}"
    return True, str(dest)


def needs_image(folder: str) -> bool:
    d = REPO / "blog" / folder
    if not d.is_dir():
        return False
    if not (d / "index-en.qmd").exists():
        return False
    for ext in (".jpg", ".jpeg", ".png"):
        if any(d.glob(f"*{ext}")):
            return False
    return True


def first_missing_image() -> str | None:
    blog = REPO / "blog"
    folders = sorted(p.name for p in blog.iterdir() if p.is_dir() and re.fullmatch(r"\d{8}", p.name))
    for folder in folders:
        if needs_image(folder):
            return folder
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=["copy-prompt", "finalize", "needs-image", "first-missing"],
    )
    parser.add_argument("folder", nargs="?", default="")
    args = parser.parse_args()

    if args.command == "copy-prompt":
        if not args.folder:
            print("folder required", file=sys.stderr)
            sys.exit(1)
        path = copy_prompt(args.folder)
        print(path)
    elif args.command == "needs-image":
        if not args.folder:
            print("folder required", file=sys.stderr)
            sys.exit(1)
        print("yes" if needs_image(args.folder) else "no")
    elif args.command == "first-missing":
        result = first_missing_image()
        if result:
            print(result)
        else:
            print("none")
    elif args.command == "finalize":
        if not args.folder:
            print("folder required", file=sys.stderr)
            sys.exit(1)
        ok, msg = finalize(args.folder)
        if ok:
            print(msg)
        else:
            print(msg, file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
