import argparse
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:
    raise ImportError(
        "Pillow is required to run this script. Install it with: python -m pip install pillow"
    ) from exc

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
TARGET_SIZE = (664, 548)


def find_image_file(source_dir: Path) -> Path:
    for entry in source_dir.iterdir():
        if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS:
            return entry
    raise FileNotFoundError(
        f"No JPG or PNG file found in source folder: {source_dir}"
    )


def build_target_path(target_dir: Path, source_path: Path) -> Path:
    target_dir_name = target_dir.name
    target_name = f"title_{target_dir_name}{source_path.suffix.lower()}"
    return target_dir / target_name


def resize_image(source_path: Path, target_path: Path) -> None:
    with Image.open(source_path) as img:
        resized = img.resize(TARGET_SIZE, Image.LANCZOS)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        resized.save(target_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize a JPG or PNG in a folder to 664x548 and save it to a target folder."
    )
    parser.add_argument(
        "target_folder",
        type=Path,
        help="Destination folder for the resized image",
    )
    parser.add_argument(
        "source_folder",
        nargs="?",
        type=Path,
        default=Path("post_source"),
        help="Folder containing a JPG or PNG file to resize (default: post_source)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_dir = args.source_folder
    target_dir = args.target_folder

    if not source_dir.exists() or not source_dir.is_dir():
        raise FileNotFoundError(f"Source folder does not exist: {source_dir}")

    source_image = find_image_file(source_dir)
    target_image = build_target_path(target_dir, source_image)
    resize_image(source_image, target_image)
    print(f"Resized image saved to: {target_image}")


if __name__ == "__main__":
    main()
