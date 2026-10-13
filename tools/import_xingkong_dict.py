#!/usr/bin/env python3
"""Merge dict/xingkong/*.txt (English=中文) into dict/ui.display.zh.json.

Also writes a machine-readable protected-key list for the hook.
Does not overwrite existing JSON values unless --force.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XINGKONG = ROOT / "dict" / "xingkong"
OUT_JSON = ROOT / "dict" / "ui.display.zh.json"
PROTECTED_OUT = ROOT / "dict" / "ui.protected.json"

# Menu access-key forms: "_File" / "P_review" → also register bare display keys
UNDERSCORE_RE = re.compile(r"_([A-Za-z])")


def parse_txt(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        en, zh = line.split("=", 1)
        en, zh = en.strip(), zh.strip()
        if not en or not zh:
            continue
        out[en] = zh
        # Also map without menu underscores: "_File" → "File"
        if "_" in en:
            bare = en.replace("_", "")
            if bare and bare not in out:
                out[bare] = zh
            # AccessText style: keep letter but drop underscore marker positions
            soft = UNDERSCORE_RE.sub(r"\1", en).lstrip("_")
            if soft and soft not in out:
                out[soft] = zh
    return out


def load_protected() -> list[str]:
    md = XINGKONG / "00_PROTECTED.md"
    if not md.exists():
        return []
    keys: list[str] = []
    in_fence = False
    for line in md.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        for tok in re.split(r"\s+", line.strip()):
            if tok and re.fullmatch(r"[A-Za-z0-9_\-]+", tok):
                keys.append(tok)
    return sorted(set(keys))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="Overwrite existing JSON values")
    args = ap.parse_args()

    if not XINGKONG.is_dir():
        raise SystemExit(f"Missing {XINGKONG}")

    merged: dict[str, str] = {}
    if OUT_JSON.exists():
        merged = json.loads(OUT_JSON.read_text(encoding="utf-8"))

    added = updated = 0
    for path in sorted(XINGKONG.glob("*.txt")):
        chunk = parse_txt(path)
        for k, v in chunk.items():
            if k not in merged:
                merged[k] = v
                added += 1
            elif args.force and merged[k] != v:
                merged[k] = v
                updated += 1

    OUT_JSON.write_text(
        json.dumps(dict(sorted(merged.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    protected = load_protected()
    PROTECTED_OUT.write_text(
        json.dumps({"iconGlyphKeys": protected}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"json_keys={len(merged)} added={added} updated={updated} protected={len(protected)}")


if __name__ == "__main__":
    main()
