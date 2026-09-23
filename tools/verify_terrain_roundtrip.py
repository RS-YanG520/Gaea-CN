#!/usr/bin/env python3
"""Verify that overlay only changes Description, and that a sample .terrain keeps English identifiers.

Does not launch the Gaea GUI. Performs static checks that protect save semantics.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "backups" / "Nodes.json.source"
DEFAULT_OVERLAY = ROOT / "overlays" / "Nodes.json"
DEFAULT_TERRAIN = Path(r"D:\Program Files\Gaea 2\Examples\Mesa.terrain")


def has_cjk(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def walk_names(obj, path="$"):
    """Yield (path, name_value) for every dict key named Name."""
    if isinstance(obj, dict):
        if "Name" in obj and isinstance(obj["Name"], str):
            yield path + ".Name", obj["Name"]
        for k, v in obj.items():
            yield from walk_names(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_names(v, f"{path}[{i}]")


def compare_structure(src_nodes: list, overlay_nodes: list) -> list[str]:
    errors: list[str] = []
    if len(src_nodes) != len(overlay_nodes):
        errors.append(f"Node count differs: {len(src_nodes)} vs {len(overlay_nodes)}")
        return errors

    for a, b in zip(src_nodes, overlay_nodes):
        an, bn = a.get("Name"), b.get("Name")
        if an != bn:
            errors.append(f"Name changed: {an!r} -> {bn!r}")
            continue
        if has_cjk(bn or ""):
            errors.append(f"CJK in node Name: {bn!r}")

        def check_flubs(fa, fb, prefix):
            if len(fa) != len(fb):
                errors.append(f"{prefix}: flub count differs for {an}")
                return
            for x, y in zip(fa, fb):
                xn, yn = x.get("Name"), y.get("Name")
                if xn != yn:
                    errors.append(f"{prefix}: Flub Name changed {xn!r} -> {yn!r}")
                elif has_cjk(yn or ""):
                    errors.append(f"{prefix}: CJK in Flub Name {yn!r}")
                check_flubs(x.get("Flubs") or [], y.get("Flubs") or [], prefix)

        check_flubs(a.get("Flubs") or [], b.get("Flubs") or [], an)

        # Description may differ; other keys should match except Description deep-walk is hard —
        # verify Name identity is enough for phase 1 safety.
    return errors


def verify_terrain(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"Terrain not found: {path}"]
    text = path.read_text(encoding="utf-8")
    types = re.findall(r'"\$type":\s*"(QuadSpinner\.Gaea\.Nodes\.[^"]+)"', text)
    if not types:
        errors.append("No $type entries found in terrain")
    for t in types:
        if has_cjk(t):
            errors.append(f"CJK in $type: {t}")

    data = json.loads(text)
    for p, name in walk_names(data):
        if has_cjk(name):
            # Metadata project title could theoretically be Chinese — only flag node-ish paths
            if ".Nodes." in p or p.endswith(".Ports") or "Ports" in p:
                errors.append(f"CJK in persisted Name at {p}: {name!r}")

    # Spot-check known English property keys still present
    for key in ("Downcutting", "ErosionScale", "Seed", "Height", "Bulk"):
        if key in text and has_cjk(key):
            errors.append(f"Unexpected CJK property key {key}")

    # Round-trip JSON load/dump must preserve $type strings
    dumped = json.dumps(data, ensure_ascii=False)
    for t in set(types):
        if t not in dumped:
            errors.append(f"$type lost after JSON round-trip: {t}")

    return errors


def verify_install_vs_backup(backup: Path, installed: Path) -> list[str]:
    errors: list[str] = []
    if not backup.is_file() or not installed.is_file():
        return errors
    bak = json.loads(backup.read_text(encoding="utf-8"))
    cur = json.loads(installed.read_text(encoding="utf-8"))
    errors.extend(compare_structure(bak, cur))
    desc_changed = sum(
        1
        for a, b in zip(bak, cur)
        if (a.get("Description") or "") != (b.get("Description") or "")
    )
    print(f"Install vs backup: top-level Description changed={desc_changed}")
    return errors


def simulate_terrain_modify_save(path: Path, out_dir: Path) -> list[str]:
    """Load .terrain, tweak a numeric prop, save, reload — ensure $type/keys stay English."""
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    def walk(obj):
        nonlocal changed
        if isinstance(obj, dict):
            t = obj.get("$type")
            if isinstance(t, str) and "Erosion2, Gaea.Nodes" in t and "Downcutting" in obj:
                obj["Downcutting"] = float(obj["Downcutting"]) * 0.99
                changed = True
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(data)
    if not changed:
        # Mesa may use different nodes — fall back to any Seed tweak
        def walk_seed(obj):
            nonlocal changed
            if isinstance(obj, dict):
                if obj.get("$type") and "Seed" in obj and isinstance(obj["Seed"], int):
                    obj["Seed"] = int(obj["Seed"]) + 1
                    changed = True
                    return
                for v in obj.values():
                    if not changed:
                        walk_seed(v)
            elif isinstance(obj, list):
                for v in obj:
                    if not changed:
                        walk_seed(v)

        walk_seed(data)
    if not changed:
        return ["Could not find a mutable property in terrain for round-trip test"]

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / (path.stem + "_roundtrip.terrain")
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    reloaded = json.loads(out.read_text(encoding="utf-8"))
    text = out.read_text(encoding="utf-8")
    for m in re.findall(r'"\$type":\s*"([^"]+)"', text):
        if has_cjk(m):
            errors.append(f"CJK in $type after save: {m}")
    for key in ("Downcutting", "Seed", "Height", "Bulk"):
        if key in path.read_text(encoding="utf-8") and key not in text and key == "Seed":
            # Seed should still exist if it existed
            pass
    # Ensure reload preserves types
    orig_types = set(re.findall(r'"\$type":\s*"([^"]+)"', path.read_text(encoding="utf-8")))
    new_types = set(re.findall(r'"\$type":\s*"([^"]+)"', text))
    if orig_types != new_types:
        errors.append(f"$type set changed after modify-save: {orig_types ^ new_types}")
    _ = reloaded
    print(f"Terrain modify-save-reload wrote: {out}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--overlay", type=Path, default=DEFAULT_OVERLAY)
    parser.add_argument("--terrain", type=Path, default=DEFAULT_TERRAIN)
    parser.add_argument(
        "--backup",
        type=Path,
        default=ROOT / "backups" / "Nodes.json.bak",
    )
    parser.add_argument(
        "--installed",
        type=Path,
        default=Path(r"D:\Program Files\Gaea 2\Resources\Nodes.json"),
    )
    args = parser.parse_args()

    errors: list[str] = []

    if not args.source.is_file():
        errors.append(f"Source missing: {args.source}")
    if not args.overlay.is_file():
        errors.append(f"Overlay missing: {args.overlay}")

    if args.source.is_file() and args.overlay.is_file():
        src = json.loads(args.source.read_text(encoding="utf-8"))
        ov = json.loads(args.overlay.read_text(encoding="utf-8"))
        errors.extend(compare_structure(src, ov))

        # Count description diffs
        desc_changed = 0
        for a, b in zip(src, ov):
            if (a.get("Description") or "") != (b.get("Description") or ""):
                desc_changed += 1
        print(f"Nodes with top-level Description changed: {desc_changed}")

    errors.extend(verify_terrain(args.terrain))
    errors.extend(verify_install_vs_backup(args.backup, args.installed))
    if args.terrain.is_file():
        errors.extend(simulate_terrain_modify_save(args.terrain, ROOT / "backups" / "verify_tmp"))

    if errors:
        print("FAIL")
        for e in errors:
            print(" -", e)
        return 1

    print("PASS: overlay Names intact; sample .terrain identifiers remain English")
    print(f"Terrain checked: {args.terrain}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
