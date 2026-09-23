#!/usr/bin/env python3
"""Add remaining English UI strings from Options / menus / tips."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Tips / help paragraphs (exact matches)
    "It is critical that any of these folders are not in a subfolder where Gaea is installed. For example, if you install in D:\\Gaea\\ you should not have your projects or documents as D:\\Gaea\\Docs": "重要：这些文件夹不能放在 Gaea 安装目录的子文件夹中。例如安装在 D:\\Gaea\\ 时，不要把工程或文档放在 D:\\Gaea\\Docs。",
    "Projects are usually small, lightweight files. However, Builds are very large and heavy. Keeping them separate is recommended if you frequently backup either folder.": "工程文件通常较小、较轻；构建结果则很大很重。若经常备份其中任一文件夹，建议分开存放。",
    "You can drop a connection on the middle of a node, and select 'Add as Mask' to add a Mask Port, instead of enabling this legacy option.": "可将连线拖到节点中部，并选择「添加为遮罩」来添加遮罩端口，而不必启用此旧选项。",
    "This is the new and recommended way of working in Gaea. (Existing nodes and files will not be affected)": "这是 Gaea 中推荐的新工作方式。（现有节点与文件不受影响）",
    "This is where output files from builds are stored. It is denoted by the <Builds> token in Build Settings > Destination.": "构建输出文件存放于此。在「构建设置 > 目标」中用 <Builds> 标记表示。",
    "2K or 4K cache is offloaded from RAM to disk if unaccessed for the Idle Threshold. Cache is instantly loaded back to memory when required.": "若超过空闲阈值未被访问，2K/4K 缓存会从内存卸载到磁盘；需要时会立即重新载入内存。",
    "This is recommended when using SSD storage.": "建议在使用 SSD 存储时开启。",
    "Recommend using SSD for Cache location.": "建议将缓存位置放在 SSD 上。",
    "Save in Central Cache Folder": "保存到中央缓存文件夹",
    "Will save next to file in \\Cache subfolder when disabled.": "关闭时将保存到文件旁的 \\Cache 子文件夹。",
    "This preview feature allows the Gaea engine to free up RAM more quickly. If you experience instability in general, or crashes, you should disable this feature.": "此预览功能可让 Gaea 引擎更快释放内存。若出现不稳定或崩溃，请关闭此功能。",
    "This reduces clutter in the directory tree. You can still access any location by typing a path, or using the breadcrumbs at the top.": "这样可减少目录树杂乱。仍可通过输入路径或顶部面包屑访问任意位置。",
    # Partial labels still English
    "Search Results": "搜索结果",
    "Maximum Result": "最大结果数",
    "seconds": "秒",
    "TileInput": "平铺输入",
    "WaveShine": "波光",
    "Primitive": "基础体",
    "Copy Properties": "复制属性",
    "Paste Properties": "粘贴属性",
    # Graph menu
    "New Graph Tab": "新建节点图标签",
    "Add Note": "添加注释",
    "Extents": "范围适应",
    "Reset Zoom": "重置缩放",
    "Selection": "选中适应",
    "Graph Surface": "节点图表面",
    "Snap to Grid": "吸附到网格",
    "Snap to Items": "吸附到对象",
    "Bake": "烘焙",
    "Bookmarks": "书签",
    "Add bookmark": "添加书签",
    # Bake submenu
    "Bake Selected": "烘焙所选",
    "Bake Required Nodes": "烘焙所需节点",
    "Force load baked cache": "强制加载烘焙缓存",
    "Unbake Selected": "取消烘焙所选",
    "Unbake All": "全部取消烘焙",
    "Resolution": "分辨率",
    "Cache to Disk": "缓存到磁盘",
    "When closing file": "关闭文件时",
    "When Idle": "空闲时",
    "Delete Cache": "删除缓存",
    # Node menu
    "Refresh": "刷新",
    "Lock Preview to Node": "将预览锁定到节点",
    "Mark for Export": "标记为导出",
    "Mutate": "变异",
    "Locked 2D Viewport": "锁定二维视口",
    "Select Upstream": "选择上游",
    "Select Downstream": "选择下游",
    "Group / Ungroup": "编组 / 解组",
    "Combine nodes": "合并节点",
    "Convert port to portals": "将端口转为传送门",
    "Move to Tab": "移动到标签",
    "Presets": "预设",
    # Toolbox family headers (ensure present)
    "ASSETS": "资产",
    "BASIC": "基础",
    "EXTENDED": "扩展",
    "GRADIENT": "渐变",
    "LANDSCAPE": "地貌",
    "PRIMITIVE": "基础体",
    # Misc already partially translated siblings
    "Object": "对象",
    "File": "文件",
    "Cracks": "裂纹",
    "Draw": "绘制",
    "Noise": "噪声",
    "Pattern": "图案",
    "Shape": "形状",
    "Constant": "常量",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    before = len(data)
    data.update(ADD)

    # Also register tip variants that may include backticks/path punctuation differences
    tip_variants = {
        "It is critical that any of these folders are not in a subfolder where Gaea is installed. For example, if you install in D:\\Gaea\\ you should not have your projects or documents as D:\\Gaea\\Docs": ADD[
            "It is critical that any of these folders are not in a subfolder where Gaea is installed. For example, if you install in D:\\Gaea\\ you should not have your projects or documents as D:\\Gaea\\Docs"
        ],
    }
    data.update(tip_variants)

    extra = {}
    for k, v in list(data.items()):
        if k.endswith("..."):
            extra[k[:-3] + "…"] = v
    data.update(extra)

    PATH.write_text(
        json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {PATH}: {before} -> {len(data)} (+{len(data) - before})")


if __name__ == "__main__":
    main()
