#!/usr/bin/env python3
"""Seed leftovers from Flow / Erosion2 / file-menu screenshots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    "Precipitation": "降水",
    "Precipita...": "降水",
    "Precipita…": "降水",
    "Flow Length": "流向长度",
    "Flow Volume": "流向体积",
    "Flow (FlowMap)": "流向（流向图）",
    "FlowMap": "流向图",
    "Downcutting": "下切",
    "Selective Processing": "选择性处理",
    "Duration": "持续时间",
    "Rock Softness": "岩石柔软度",
    "Strength": "强度",
    "Inhibition": "抑制",
    "Base Level": "基准高度",
    "Volume": "体积",
    "Area Effect": "区域效果",
    "Erosion Strength": "侵蚀强度",
    "Precipitation Amount": "降水量",
    "Other Settings": "其他设置",
    "Aggressive Mode": "激进模式",
    "Deterministic": "确定性",
    "Information": "说明",
    "Erosion2 is the recommended Erosion node. Erosion is still a very powerful but uses older technology and may be unable to produce similar results.": "推荐使用 Erosion2 侵蚀节点。旧版 Erosion 仍然很强，但技术较旧，可能无法得到相近效果。",
    "TORLET...": "TORLET...",
    "TORLET…": "TORLET...",
    "Image...": "图像...",
    "Image…": "图像...",
    "Recent Files": "最近文件",
    "Open Autosave...": "打开自动保存...",
    "Open Autosave…": "打开自动保存...",
    'You can drop a connection on the middle of a node, and select "Add as Mask" to add a Mask Port, instead of enabling this legacy option.': "可将连线拖到节点中央，并选择「添加为遮罩」来添加遮罩端口，无需启用此旧版选项。",
    "You can drop a connection on the middle of a node, and select “Add as Mask” to add a Mask Port, instead of enabling this legacy option.": "可将连线拖到节点中央，并选择「添加为遮罩」来添加遮罩端口，无需启用此旧版选项。",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    added = 0
    for k, v in ADD.items():
        if k not in data:
            data[k] = v
            added += 1
    PATH.write_text(
        json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"keys={len(data)} added={added}")


if __name__ == "__main__":
    main()
