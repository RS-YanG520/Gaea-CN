#!/usr/bin/env python3
"""Batch-add node menus / context / props / styles from latest screenshots."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Category headers still English
    "EFFECT": "效果",
    "PROFILE": "曲线配置",
    "UTILITIES": "实用工具",
    "ROCKY": "岩层",
    "SCATTER": "散布",
    "SUPERFICIAL": "表层",
    "TERRACE": "阶地",
    "VEGETATION": "植被",
    "WATER": "水体",
    "Primitive": "基础体",
    "PRIMITIVE": "基础体",
    # Leftover node labels
    "Uplift": "抬升",
    "Swirl": "漩涡",
    "Whorl": "涡旋",
    "ThermalShaper": "热力塑形",
    "Transpose": "转置",
    "Wizard": "向导",
    "Wizard2": "向导2",
    # Command palette categories (dim labels)
    "Assets": "资产",
    "Adjust": "调整",
    "Erosion": "侵蚀",
    "Color": "颜色",
    "Routing": "路由",
    # Context menu (graph / node)
    "Rename": "重命名",
    "Duplicate": "复制",
    "Bypass": "旁通",
    "Bookmark": "书签",
    "Lock Preview": "锁定预览",
    "Use as Underlay": "用作衬底",
    "Exclude from Underlay": "从衬底排除",
    "Mark for Export": "标记为导出",
    "Replace": "替换",
    "Insert chokepoint": "插入卡点",
    "Manage Portals": "管理传送门",
    "Copy Properties": "复制属性",
    "Paste Properties": "粘贴属性",
    "Show Locked 2D Viewport": "显示锁定的二维视口",
    "Select upstream": "选择上游",
    "Select downstream": "选择下游",
    "Select Upstream": "选择上游",
    "Select Downstream": "选择下游",
    "Reset": "重置",
    "New Graph": "新建节点图",
    "Node Bookmarks": "节点书签",
    "Add a variable using the button above.": "使用上方按钮添加变量。",
    # Ports / data kinds
    "Flow": "水流",
    "Wear": "磨损",
    "Deposits": "沉积",
    "Out": "输出",
    "Heightfield": "高度场",
    "Mask": "遮罩",
    "Built": "已构建",
    "Build Time": "构建时间",
    "Min": "最小",
    "Max": "最大",
    "Range": "范围",
    "Size": "大小",
    "ID": "ID",
    # Bake / engine
    "Bake Selected": "烘焙所选",
    "Reload SmartCache to RAM": "将 SmartCache 重新加载到内存",
    "Suspend Engine (Currently running)": "挂起引擎（当前运行中）",
    "Suspend Engine (Currently suspended)": "恢复引擎（当前已挂起）",
    "Suspend Engine": "挂起引擎",
    "Resume Engine": "恢复引擎",
    "Engine Active": "引擎已启用",
    # Quick adjust / mask tools
    "Influence": "影响",
    "Difference": "差值",
    "Mask by Slope": "按坡度遮罩",
    "Mask by Height": "按高度遮罩",
    "Match Height": "匹配高度",
    "Strong": "强",
    # Property panel
    "Style": "样式",
    "Style Editor": "样式编辑器",
    "Bias Angle": "偏向角",
    "Seed": "随机种子",
    "Height Remap": "高度重映射",
    "Simple": "简单",
    # Erosion style presets
    "Ancient": "古老",
    "Ancient 2": "古老 2",
    "Alpine": "高山",
    "Rocky": "岩质",
    "Exposed": "裸露",
    "Flows": "水流",
    "Flows 2": "水流 2",
    "Flows 3": "水流 3",
    "Strata": "岩层",
    "Withered": "风化",
    "Soft Soil": "软土",
    "Soft Soil 2": "软土 2",
    "Dessicated": "干涸",
    "Thin": "薄层",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    before = len(data)
    data.update(ADD)
    extra = {}
    for k, v in list(data.items()):
        c = re.sub(r"\s+", " ", k).strip()
        if c != k:
            extra[c] = v
        if k.endswith("..."):
            extra[k[:-3] + "…"] = v
    data.update(extra)
    PATH.write_text(
        json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"{before} -> {len(data)} (+{len(data) - before})")


if __name__ == "__main__":
    main()
