#!/usr/bin/env python3
"""Extract translatable Description fields from Gaea Nodes.json into a zh dictionary skeleton.

Never extracts Name fields for translation — Names stay English identifiers.
Always prefer English backups over the install copy (which may already be localized).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SOURCE = Path(r"D:\Program Files\Gaea 2\Resources\Nodes.json")
BACKUP_BAK = ROOT / "backups" / "Nodes.json.bak"
BACKUP_SOURCE = ROOT / "backups" / "Nodes.json.source"
OUT_PATH = ROOT / "dict" / "nodes.descriptions.zh.json"


def resolve_english_source() -> Path:
    """Prefer English backups — never re-extract from an already-localized install copy."""
    for path in (BACKUP_BAK, BACKUP_SOURCE, INSTALL_SOURCE):
        if path.is_file():
            return path
    raise SystemExit("No Nodes.json source found (backups/ or install Resources)")


def looks_cjk(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def load_nodes(source: Path) -> list:
    with source.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise SystemExit(f"Expected Nodes.json array, got {type(data)}")
    return data


def extract_flub(flub: dict) -> dict | None:
    entry: dict = {}
    desc = flub.get("Description") or ""
    if desc:
        entry["en"] = desc
        entry["zh"] = ""

    nested = flub.get("Flubs") or []
    values: dict = {}
    for child in nested:
        name = child.get("Name")
        if not name:
            continue
        child_entry = extract_flub(child)
        if child_entry:
            values[name] = child_entry
    if values:
        entry["values"] = values

    return entry or None


def extract_node(node: dict) -> dict | None:
    name = node.get("Name")
    if not name:
        return None
    entry: dict = {}
    desc = node.get("Description") or ""
    if desc:
        entry["en"] = desc
        entry["zh"] = ""

    flubs_out: dict = {}
    for flub in node.get("Flubs") or []:
        fname = flub.get("Name")
        if not fname:
            continue
        fentry = extract_flub(flub)
        if fentry:
            flubs_out[fname] = fentry
    if flubs_out:
        entry["flubs"] = flubs_out

    return (name, entry) if entry else None


def merge_existing_zh(new_dict: dict, old_dict: dict) -> None:
    """Preserve already-filled zh translations when re-extracting."""
    old_nodes = (old_dict or {}).get("nodes") or {}
    for nname, nentry in new_dict["nodes"].items():
        old = old_nodes.get(nname)
        if not old:
            continue
        old_zh = (old.get("zh") or "").strip()
        old_en = old.get("en") or ""
        if old_zh:
            nentry["zh"] = old_zh
        elif looks_cjk(old_en) and not looks_cjk(nentry.get("en") or ""):
            # Previous extract wrongly stored Chinese in `en`
            nentry["zh"] = old_en
        merge_flubs_zh(nentry.get("flubs") or {}, old.get("flubs") or {})


def merge_flubs_zh(new_flubs: dict, old_flubs: dict) -> None:
    for fname, fentry in new_flubs.items():
        old = old_flubs.get(fname)
        if not old:
            continue
        old_zh = (old.get("zh") or "").strip()
        old_en = old.get("en") or ""
        if old_zh:
            fentry["zh"] = old_zh
        elif looks_cjk(old_en) and not looks_cjk(fentry.get("en") or ""):
            fentry["zh"] = old_en
        merge_flubs_zh(fentry.get("values") or {}, old.get("values") or {})


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract Description dictionary from Nodes.json")
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Path to original English Nodes.json (defaults to backups, not install)",
    )
    parser.add_argument("--out", type=Path, default=OUT_PATH, help="Output dictionary path")
    args = parser.parse_args()
    if args.source is None:
        args.source = resolve_english_source()

    if not args.source.is_file():
        raise SystemExit(f"Source not found: {args.source}")

    if looks_cjk(args.source.read_text(encoding="utf-8")[:2000]):
        print(f"WARNING: source may already contain Chinese: {args.source}")

    nodes = load_nodes(args.source)
    out = {
        "version": 1,
        "policy": "Translate only Description (zh). Never change Name / EnumValue keys.",
        "source": str(args.source),
        "nodeCount": len(nodes),
        "nodes": {},
    }

    for node in nodes:
        extracted = extract_node(node)
        if extracted:
            name, entry = extracted
            out["nodes"][name] = entry

    if args.out.is_file():
        with args.out.open(encoding="utf-8") as f:
            old = json.load(f)
        merge_existing_zh(out, old)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

    translated = sum(1 for n in out["nodes"].values() if (n.get("zh") or "").strip())
    print(f"Source: {args.source}")
    print(f"Wrote {args.out}")
    print(f"Nodes with any description entry: {len(out['nodes'])}")
    print(f"Nodes with zh filled: {translated}")


if __name__ == "__main__":
    main()
