#!/usr/bin/env python3
"""Merge dict/nodes.descriptions.zh.json into a copy of Nodes.json → overlays/Nodes.json.

Only Description fields are overwritten when zh is non-empty. All Name fields stay English.
Builds from English backups, not from an already-localized install copy.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL_SOURCE = Path(r"D:\Program Files\Gaea 2\Resources\Nodes.json")
BACKUP_BAK = ROOT / "backups" / "Nodes.json.bak"
BACKUP_SOURCE = ROOT / "backups" / "Nodes.json.source"
DICT_PATH = ROOT / "dict" / "nodes.descriptions.zh.json"
OUT_PATH = ROOT / "overlays" / "Nodes.json"


def resolve_english_source() -> Path:
    for path in (BACKUP_BAK, BACKUP_SOURCE, INSTALL_SOURCE):
        if path.is_file():
            return path
    raise SystemExit("No Nodes.json source found")


def apply_flub_descriptions(flub: dict, entry: dict | None) -> int:
    if not entry:
        return 0
    changed = 0
    zh = (entry.get("zh") or "").strip()
    if zh:
        flub["Description"] = zh
        changed += 1
    values = entry.get("values") or {}
    for child in flub.get("Flubs") or []:
        cname = child.get("Name")
        if cname and cname in values:
            changed += apply_flub_descriptions(child, values[cname])
    return changed


def apply_node_descriptions(node: dict, entry: dict | None) -> int:
    if not entry:
        return 0
    changed = 0
    zh = (entry.get("zh") or "").strip()
    if zh:
        node["Description"] = zh
        changed += 1
    flubs_dict = entry.get("flubs") or {}
    for flub in node.get("Flubs") or []:
        fname = flub.get("Name")
        if fname and fname in flubs_dict:
            changed += apply_flub_descriptions(flub, flubs_dict[fname])
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Build overlays/Nodes.json from zh dictionary")
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--dict", type=Path, default=DICT_PATH)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()
    if args.source is None:
        args.source = resolve_english_source()

    if not args.source.is_file():
        raise SystemExit(f"Source not found: {args.source}")
    if not args.dict.is_file():
        raise SystemExit(f"Dictionary not found: {args.dict}")

    with args.source.open(encoding="utf-8") as f:
        nodes = json.load(f)
    with args.dict.open(encoding="utf-8") as f:
        dictionary = json.load(f)

    print(f"Building from English source: {args.source}")

    by_name = dictionary.get("nodes") or {}
    total = 0
    for node in nodes:
        name = node.get("Name")
        total += apply_node_descriptions(node, by_name.get(name))

    for node in nodes:
        name = node.get("Name") or ""
        if any("\u4e00" <= ch <= "\u9fff" for ch in name):
            raise SystemExit(f"Safety fail: Chinese found in node Name: {name!r}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(nodes, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Wrote {args.out}")
    print(f"Descriptions replaced: {total}")


if __name__ == "__main__":
    main()
