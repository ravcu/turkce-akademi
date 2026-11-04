#!/usr/bin/env python3
"""Ensure newly added or changed Türkçe Akademi learning pages load the common student progress agent.
Usage: python3 tools/ensure_auto_progress.py [path/to/file.html ...]
No arguments = audit all tracked teaching HTML files in the repository.
This tool does not change activities' scoring logic or take private student data.
"""
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TAG = '<script src="/turkce-akademi/assets/js/ta-progress-auto.js" defer></script>'
SKIP = {"ogrenci-girisi.html", "basari-sertifikasi.html"}
IN_HEAD = re.compile(r"<head\b[^>]*>", re.IGNORECASE)


def eligible(path: pathlib.Path) -> bool:
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        return False
    if path.suffix.lower() not in {".html", ".htm"} or path.name in SKIP:
        return False
    if relative.parts[0] in {".git", "tools", "docs", "archive", "vendor", "node_modules"}:
        return False
    # All books and educational activities, not home, auth, technical previews.
    return relative.parts[0] == "kitaplar" or (
        len(relative.parts) == 1
        and bool(re.search(r"(?:etkinlik|okuma|dinleme|konusma|yazma|kelime|test|quiz)", path.name, re.I))
    )


def inject(path: pathlib.Path) -> str:
    try:
        src = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return "unreadable"
    if "ta-progress-auto.js" in src or "media-loader.js" in src:
        # media-loader.js bootstraps the same automatic module.
        return "already-covered"
    match = IN_HEAD.search(src)
    if not match:
        return "no-head"
    src = src[:match.end()] + "\n" + TAG + src[match.end():]
    path.write_text(src, encoding="utf-8")
    return "updated"


def main() -> int:
    if len(sys.argv) > 1:
        names = sys.argv[1:]
    else:
        names = subprocess.check_output(
            ["git", "ls-files", "*.html", "*.htm"], cwd=ROOT, text=True
        ).splitlines()
    failures = []
    updated = []
    for name in names:
        path = (ROOT / name).resolve()
        if not path.is_file() or not eligible(path):
            continue
        result = inject(path)
        print(f"{result}: {path.relative_to(ROOT)}")
        if result == "updated":
            updated.append(path)
        elif result not in {"already-covered"}:
            failures.append((path, result))
    print(f"auto-progress: instrumented={len(updated)}, failed={len(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
