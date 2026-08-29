#!/usr/bin/env python3
"""Compress large raster images in Pelican output/ to WebP before deploy.

Keeps source files in content/ untouched. After `pelican` copies them into
output/, oversized JPEG/PNG/WebP stills are resized (max width) and encoded
as WebP. Generated HTML/XML/CSS is rewritten to the new filenames, and the
heavy originals are removed from output/ so they are not rsynced live.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

MAX_WIDTH = 1400
QUALITY = 80
# Skip files that are already small *and* within the width cap.
MIN_BYTES = 80 * 1024
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
REWRITE_EXTS = {".html", ".xml", ".css", ".js", ".json", ".txt"}
SKIP_DIR_PARTS = {"font-awesome", "pygments", "tipuesearch", "stork"}


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def which_cwebp() -> str:
    path = shutil.which("cwebp")
    if not path:
        die("cwebp not found; install with: brew install webp")
    return path


def is_animated_webp(path: Path) -> bool:
    try:
        data = path.read_bytes()[: 64 * 1024]
    except OSError:
        return False
    return data[:4] == b"RIFF" and b"ANIM" in data


def pixel_width(path: Path) -> int | None:
    sips = shutil.which("sips")
    if not sips:
        return None
    try:
        out = subprocess.check_output(
            [sips, "-g", "pixelWidth", str(path)],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("pixelWidth:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def human_size(n: int) -> str:
    if n < 1024:
        return f"{n}B"
    if n < 1024 * 1024:
        return f"{n / 1024:.0f}K"
    return f"{n / (1024 * 1024):.1f}M"


def should_skip_dir(path: Path, root: Path) -> bool:
    try:
        parts = set(path.relative_to(root).parts[:-1])
    except ValueError:
        return True
    return bool(parts & SKIP_DIR_PARTS)


def iter_images(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_PARTS]
        base = Path(dirpath)
        for name in filenames:
            path = base / name
            if path.suffix.lower() in IMAGE_EXTS:
                yield path


def needs_compress(path: Path) -> bool:
    size = path.stat().st_size
    width = pixel_width(path)
    if width is not None and width > MAX_WIDTH:
        return True
    # Already-WebP files at the target width are left alone so publish is
    # idempotent. Fat still WebPs (e.g. lossless) still get a second pass.
    if path.suffix.lower() == ".webp":
        return size >= 500 * 1024
    return size >= MIN_BYTES


def encode_webp(cwebp: str, src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".tmp")
    cmd = [
        cwebp,
        "-quiet",
        "-mt",
        "-q",
        str(QUALITY),
        "-resize",
        str(MAX_WIDTH),
        "0",
        "-resize_mode",
        "down_only",
        str(src),
        "-o",
        str(tmp),
    ]
    subprocess.check_call(cmd)
    tmp.replace(dest)


def rewrite_refs(root: Path, replacements: list[tuple[str, str]]) -> int:
    """Replace original image paths with .webp in generated text files."""
    if not replacements:
        return 0
    touched = 0
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in REWRITE_EXTS:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            new = text
            for old, webp in replacements:
                new = new.replace(old, webp)
            if new != text:
                path.write_text(new, encoding="utf-8")
                touched += 1
    return touched


def rel_url(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def compress_tree(root: Path, dry_run: bool = False) -> int:
    cwebp = which_cwebp()
    replacements: list[tuple[str, str]] = []
    converted = 0
    skipped = 0
    saved = 0

    print(f"==> Compressing images in {root} (max width {MAX_WIDTH}px, q={QUALITY})")

    for src in sorted(iter_images(root)):
        if should_skip_dir(src, root):
            continue
        if src.suffix.lower() == ".webp" and is_animated_webp(src):
            print(f"  skip animated  {rel_url(root, src)}")
            skipped += 1
            continue
        if not needs_compress(src):
            skipped += 1
            continue

        dest = src.with_suffix(".webp")
        if dest != src and dest.exists():
            print(f"  skip collision {rel_url(root, src)} (already have {dest.name})")
            skipped += 1
            continue

        before = src.stat().st_size
        width = pixel_width(src)
        width_note = f"{width}px" if width else "?"

        if dry_run:
            print(f"  would convert  {rel_url(root, src)}  {human_size(before)} {width_note}")
            converted += 1
            continue

        try:
            encode_webp(cwebp, src, dest)
        except subprocess.CalledProcessError as exc:
            print(f"  fail           {rel_url(root, src)} ({exc})")
            continue

        after = dest.stat().st_size
        if after >= before:
            if dest != src:
                dest.unlink(missing_ok=True)
            print(
                f"  keep original  {rel_url(root, src)}  "
                f"{human_size(before)} -> {human_size(after)} (not smaller)"
            )
            skipped += 1
            continue

        saved += before - after
        converted += 1
        print(
            f"  {rel_url(root, src)}  {human_size(before)} {width_note} "
            f"-> {rel_url(root, dest)}  {human_size(after)}"
        )

        if dest != src:
            replacements.append((rel_url(root, src), rel_url(root, dest)))
            src.unlink()

    rewritten = 0 if dry_run else rewrite_refs(root, replacements)
    print(
        f"==> Images: {converted} compressed, {skipped} skipped, "
        f"{human_size(saved)} saved, {rewritten} files rewritten"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="output",
        help="Pelican output directory (default: output)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List images that would be compressed, do not write",
    )
    args = parser.parse_args()
    root = Path(args.output_dir).resolve()
    if not root.is_dir():
        die(f"{root} does not exist; build the site first")
    return compress_tree(root, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
