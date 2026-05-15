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


def find_image_file(folder: Path) -> Path:
    for entry in folder.iterdir():
        if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS:
            return entry
    raise FileNotFoundError(
        f"No JPG or PNG file found in folder: {folder}"
    )


def resize_image_inplace(folder: Path) -> None:
    source_path = find_image_file(folder)
    target_name = f"title_{folder.name}{source_path.suffix.lower()}"
    target_path = folder / target_name

    with Image.open(source_path) as img:
        resized = img.resize(TARGET_SIZE, Image.LANCZOS)
        resized.save(target_path)

    if source_path.resolve() != target_path.resolve():
        source_path.unlink()

    print(f"Resized image saved in-place: {target_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resize a JPG or PNG in a folder to 664x548 in-place, renaming it to title_YYYYMMDD.*"
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Blog post folder containing the image to resize (e.g. blog/20260517)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    folder = args.folder

    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    resize_image_inplace(folder)


if __name__ == "__main__":
    main()
