#!/usr/bin/env python3
"""Helpers for BizKit WhatsApp channel posting workflow."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Language code → channel metadata (from BizKit channel list)
CHANNELS = {
    "en": {
        "name": "BizKit - English",
        "code": "0029VbAwFip59PwKCh7Wwi1F",
        "link_suffix": "index-en.html",
    },
    "hi": {
        "name": "BizKit - हिंदी",
        "code": "0029VbAl8ug4o7qMtawhPL30",
        "link_suffix": "index-hi.html",
    },
    "ta": {
        "name": "BizKit - தமிழ்",
        "code": "0029VbASzeEAu3aWiQPlHp04",
        "link_suffix": "index-ta.html",
    },
    "te": {
        "name": "BizKit - తెలుగు",
        "code": "0029VbB6WYg4tRropQUeJ02D",
        "link_suffix": "index-te.html",
    },
    "kn": {
        "name": "BizKit - ಕನ್ನಡ",
        "code": "0029Vb6AO5kICVfpNSqdmB2l",
        "link_suffix": "index-kn.html",
    },
    "de": {
        "name": "BizKit - Deutsch",
        "code": "0029VbBNPJ384Om4uNmKLF1r",
        "link_suffix": "index-de.html",
    },
}

POST_ORDER = ["en", "hi", "ta", "te", "kn", "de"]

SECTION_MARKERS = ("📌", "📜")


def format_whatsapp_message(text: str) -> str:
    """Ensure one blank line before 📌 and 📜 section headers."""
    lines = text.strip().splitlines()
    if not lines:
        return text
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(SECTION_MARKERS) and out and out[-1].strip():
            out.append("")
        out.append(line.rstrip())
    return "\n".join(out).strip() + "\n"


def channel_url(lang: str) -> str:
    if lang not in CHANNELS:
        raise KeyError(f"Unknown language: {lang}")
    code = CHANNELS[lang]["code"]
    return f"https://web.whatsapp.com/accept?channel_invite_code={code}"


def image_path(folder: str) -> Path:
    p = REPO / "blog" / folder / f"title_{folder}.png"
    if not p.exists():
        raise FileNotFoundError(f"Missing title image: {p}")
    return p


def copy_to_clipboard(text: str) -> None:
    if sys.platform == "darwin":
        subprocess.run(["pbcopy"], input=text, text=True, check=True)
        return

    if os.name == "nt":
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
            input=text,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return

    for command in (("wl-copy",), ("xclip", "-selection", "clipboard"), ("xsel", "--clipboard", "--input")):
        try:
            subprocess.run(command, input=text, text=True, check=True)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue


def copy_image_to_clipboard(folder: str) -> Path:
    img = image_path(folder)
    if sys.platform == "darwin":
        subprocess.run(
            [
                "osascript",
                "-e",
                f'set the clipboard to (read (POSIX file "{img}") as «class PNGf»)',
            ],
            check=True,
        )
    elif os.name == "nt":
        image_path_text = str(img).replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "Add-Type -AssemblyName System.Drawing; "
            f"$image = [System.Drawing.Image]::FromFile('{image_path_text}'); "
            "[System.Windows.Forms.Clipboard]::SetImage($image)"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    else:
        raise RuntimeError("Image clipboard copying is only implemented for macOS and Windows in this helper.")
    return img


def save_message(folder: str, lang: str, text: str) -> Path:
    out_dir = Path(tempfile.gettempdir()) / f"whatsapp_{folder}"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{lang}.txt"
    path.write_text(format_whatsapp_message(text), encoding="utf-8")
    return path


def load_message(folder: str, lang: str) -> str:
    path = Path(tempfile.gettempdir()) / f"whatsapp_{folder}" / f"{lang}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Missing message file: {path}")
    return path.read_text(encoding="utf-8")


def copy_message_to_clipboard(folder: str, lang: str) -> str:
    text = format_whatsapp_message(load_message(folder, lang))
    copy_to_clipboard(text)
    return text


def handoff_json(folder: str) -> dict:
    messages_dir = Path(tempfile.gettempdir()) / f"whatsapp_{folder}"
    messages = {}
    for lang in POST_ORDER:
        p = messages_dir / f"{lang}.txt"
        if p.exists():
            messages[lang] = p.read_text(encoding="utf-8")
    return {
        "folder": folder,
        "image": str(image_path(folder)),
        "channels": {lang: CHANNELS[lang]["name"] for lang in POST_ORDER},
        "urls": {lang: channel_url(lang) for lang in POST_ORDER},
        "messages": messages,
        "post_order": POST_ORDER,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "channel-url",
            "copy-image",
            "copy-caption",
            "format-message",
            "save-message",
            "load-message",
            "handoff",
            "list-channels",
        ],
    )
    parser.add_argument("folder", nargs="?", default="")
    parser.add_argument("--lang", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()

    if args.command == "list-channels":
        print(json.dumps(CHANNELS, indent=2, ensure_ascii=False))
        return

    if args.command == "channel-url":
        if not args.lang:
            print("--lang required", file=sys.stderr)
            sys.exit(1)
        print(channel_url(args.lang))
        return

    if args.command == "format-message":
        if args.stdin:
            raw = sys.stdin.read()
        elif args.text:
            raw = args.text
        elif args.folder and args.lang:
            raw = load_message(args.folder, args.lang)
        else:
            print("provide --stdin, --text, or folder + --lang", file=sys.stderr)
            sys.exit(1)
        print(format_whatsapp_message(raw), end="")
        return

    if not args.folder:
        print("folder (YYYYMMDD) required", file=sys.stderr)
        sys.exit(1)

    if args.command == "copy-image":
        p = copy_image_to_clipboard(args.folder)
        print(p)
    elif args.command == "copy-caption":
        if not args.lang:
            print("--lang required", file=sys.stderr)
            sys.exit(1)
        print(copy_message_to_clipboard(args.folder, args.lang), end="")
    elif args.command == "save-message":
        if not args.lang:
            print("--lang required", file=sys.stderr)
            sys.exit(1)
        if args.stdin:
            raw = sys.stdin.read()
        elif args.text:
            raw = args.text
        else:
            print("provide --stdin or --text", file=sys.stderr)
            sys.exit(1)
        p = save_message(args.folder, args.lang, raw)
        print(p)
    elif args.command == "load-message":
        if not args.lang:
            print("--lang required", file=sys.stderr)
            sys.exit(1)
        print(load_message(args.folder, args.lang), end="")
    elif args.command == "handoff":
        print(json.dumps(handoff_json(args.folder), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
