#!/usr/bin/env python3
"""Seed leftovers from SandSea / Anastomosis / Thermal / Hills screenshots."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Build status
    "Build time": "构建耗时",
    "milliseconds": "毫秒",
    "Status": "状态",
    "Built": "已构建",
    "Status: Built": "状态：已构建",
    # Sand Sea / dunes
    "Dune Type": "沙丘类型",
    "Undulation": "起伏",
    "Direction": "方向",
    "Softness": "柔软度",
    "Sharpness": "锐度",
    # Enums
    "None": "无",
    "Low": "低",
    "Medium": "中",
    "High": "高",
    "Quarter": "四分之一",
    "Third": "三分之一",
    "Half": "一半",
    "Full": "完整",
    "Moderate": "中等",
    "Aggressive": "激进",
    # Anastomosis / channels
    "Impact": "冲击",
    "Depth": "深度",
    "Quality": "质量",
    "Smooth Edges": "平滑边缘",
    "Destructive": "破坏性",
    "Pits": "坑穴",
    "Riversx 2": "河流×2",
    "Riversx 4": "河流×4",
    "Flooding": "洪水",
    "Floodingx 2": "洪水×2",
    "Flooding X4": "洪水×4",
    "Floodingx 4": "洪水×4",
    # Shatter / fracture
    "Coverage": "覆盖",
    "Horizontal": "水平",
    "Vertical": "垂直",
    "Rock Hardness": "岩石硬度",
    # Scale group
    "Feature Scale": "特征尺度",
    "Real Scale": "真实比例",
    "Erosion Scale": "侵蚀尺度",
    "No Erosion": "无侵蚀",
    # Sediment discharge
    "Sediment Discharge": "沉积物排泄",
    "Suspended Load": "悬移质",
    "Discharge Angle": "排泄角",
    "Bed Load": "推移质",
    "Coarse Sediments": "粗沉积物",
    "Deposition Boost": "沉积增强",
    # Shape / orographic
    "Shape Sharpness": "形状锐度",
    "Shape Detail Scale": "形状细节尺度",
    "Orographic Influence": "地形抬升影响",
    # Hills
    "Creep": "蠕变",
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
