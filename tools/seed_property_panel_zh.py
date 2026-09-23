#!/usr/bin/env python3
"""Seed property-panel / node-context leftovers from screenshots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Property labels
    "Scale": "缩放",
    "Height": "高度",
    "Bulk": "体量",
    "Reduce Details": "减少细节",
    "Formation": "形成度",
    "Chaos": "混沌",
    "Size": "大小",
    "Style": "样式",
    # Style / enum values
    "Old": "古老",
    "Eroded": "侵蚀",
    "Classic": "经典",
    "Low": "低",
    "Medium": "中",
    "High": "高",
    # Gizmo / chrome
    "Toggle Gizmo": "切换 Gizmo",
    # Port / binding
    "Other node...": "其他节点...",
    "Other node…": "其他节点...",
    # Presets popup
    "Create Preset": "创建预设",
    "No presets found...": "未找到预设...",
    "No presets found…": "未找到预设...",
    # Node context menu
    "Node State": "节点状态",
    "Revert Changes": "还原更改",
    "Reset to Defaults": "重置为默认",
    "Save State": "保存状态",
    "Bind all properties": "绑定全部属性",
    "Render Intent (Override)": "渲染意图（覆盖）",
    "Render Intent": "渲染意图",
    "Default": "默认",
    "Mask": "遮罩",
    "Show Help for this Node": "显示此节点帮助",
    # Tooltips
    "The randomization pattern or seed for the node's process. Changing the seed produces different crater variations.": "节点过程的随机模式或种子。更改种子可产生不同的陨石坑变体。",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    added = 0
    for k, v in ADD.items():
        if k not in data:
            data[k] = v
            added += 1
        elif data[k] != v:
            # keep existing unless empty
            pass
    PATH.write_text(
        json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"keys={len(data)} added={added}")


if __name__ == "__main__":
    main()
