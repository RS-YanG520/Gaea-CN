#!/usr/bin/env python3
"""Batch-add UI strings from Build Settings / Stats / Help / Viewport screenshots."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Statistics
    "Statistics": "统计",
    "Build Time": "构建时间",
    "Cache Size": "缓存大小",
    "Name": "名称",
    "Size in Memory": "内存占用",
    "TOTAL": "合计",
    "Click any Chart item to select a node in the List. Double-click any Chart or List item to select the node in the graph.": "单击任一图表项可选中列表中的节点；双击图表或列表项可选中节点图中的节点。",
    # Build Settings window
    "Build Settings and Regions": "构建设置与区域",
    "Build Definition": "构建定义",
    "Tiles": "分块",
    "Nodes": "节点",
    "Script": "脚本",
    "Regions": "区域",
    "Profiles": "配置档",
    "Whole Terrain": "整块地形",
    "Hybrid Subdivision": "混合细分",
    "Faster": "更快",
    "Balanced": "均衡",
    "Slower": "更慢",
    "Single Image": "单张图像",
    "Tiled Images": "分块图像",
    "Execute Build": "执行构建",
    "Copy Command Line": "复制命令行",
    "Close": "关闭",
    "Export Settings": "导出设置",
    "Build Destination": "构建目标",
    "ColorSpace": "色彩空间",
    "sRGB": "sRGB",
    "Applies to 16-bit and 8-bit RGB outputs on": "应用于 16 位与 8 位 RGB 输出",
    "Maintain a static folder with the latest copy": "维护包含最新副本的固定文件夹",
    "Open folder after build finishes": "构建完成后打开文件夹",
    "Copy the .terrain file to the build folder": "将 .terrain 文件复制到构建文件夹",
    "File overwrite mode": "文件覆盖模式",
    "Overwrite": "覆盖",
    "Increment": "递增",
    "The following tokens can be added to the Build Destination path.": "可将下列标记添加到构建目标路径。",
    "Exportable Nodes": "可导出节点",
    "Mark nodes as Exportable (F3) to see them here.": "将节点标记为可导出（F3）后会显示在此处。",
    "Post-Build Script": "构建后脚本",
    "Enter any command line instructions to execute after a successful build. The working directory will be the current build path.": "输入构建成功后要执行的命令行。工作目录为当前构建路径。",
    "Learn more": "了解更多",
    "Terrain Definition": "地形定义",
    "Width": "宽度",
    "Height": "高度",
    "Manage Regions": "管理区域",
    "Preview region": "预览区域",
    "Help": "帮助",
    "Regions require the base resolution of the terrain to be at least 4096.": "区域功能要求地形基础分辨率至少为 4096。",
    "Build Profiles": "构建配置档",
    "Load": "加载",
    # Help menu
    "User Guide": "用户指南",
    "Node Reference": "节点参考",
    "Shortcut Reference": "快捷键参考",
    "What's new in this version?": "本版本有什么新内容？",
    "Check for updates": "检查更新",
    "Manage License...": "管理许可证...",
    "Diagnostics...": "诊断...",
    "About Gaea": "关于 Gaea",
    # Lighting / visualization panel
    "Sun": "太阳",
    "Sun Azimuth": "太阳方位角",
    "Sun Elevation": "太阳高度角",
    "Visualization": "可视化",
    "Ground Brightness": "地面亮度",
    # Light section header vs Dark/Light theme — prefer theme wording; section still readable
    "Light": "亮色",
    "Exposure": "曝光",
    "Sun Intensity": "太阳强度",
    "Ambient Intensity": "环境光强度",
    "Shadows": "阴影",
    "Ambient Occlusion": "环境光遮蔽",
    "Ambient Occlu...": "环境光遮蔽",
    "Atmosphere": "大气",
    "Air Density": "空气密度",
    "Haze": "霾",
    "Ozone": "臭氧",
    "Show Skybox": "显示天空盒",
    "Fog Density": "雾密度",
    "Mask Gradient": "遮罩渐变",
    "Greyscale": "灰度",
    # Preview renderer
    "Preview Renderer": "预览渲染器",
    "Visualize Data (Render Off)": "可视化数据（关闭渲染）",
    "Clay Render": "黏土渲染",
    "Realistic Render": "真实感渲染",
    # Viewport elements
    "Viewport Elements": "视口元素",
    "Bounds": "边界",
    "Navigation Compass": "导航罗盘",
    "Overlay": "叠加",
    "Colors1": "颜色1",
    "Colors2": "颜色2",
    "Dots": "点",
    "Dark": "暗色",
    "Lines": "线",
    "Quads": "四边形",
    "UV": "UV",
    "Custom": "自定义",
    # Screenshots
    "Save Screenshot": "保存截图",
    "Screenshot Options": "截图选项",
    "Save Graph Screenshot as...": "节点图截图另存为...",
    "Save Viewport Screenshot as...": "视口截图另存为...",
    "Open Screenshots Folder": "打开截图文件夹",
    # Tools tray
    "Save to file": "保存到文件",
    "Pick Height/Color": "拾取高度/颜色",
    "Measurement Tools": "测量工具",
    # Mask enhancement
    "Mask Enhancement": "遮罩增强",
    "None / Raw": "无 / 原始",
    "Equalized": "均衡化",
    # Build extras from screenshots
    "None": "无",
    "Remove main port name in build output": "构建输出中移除主端口名",
    "Build output removes main port name": "构建输出中移除主端口名",
    "Save As...": "另存为...",
    "Delete": "删除",
    "Save": "保存",
    "Baked Cache": "烘焙缓存",
    "Bake Cache": "烘焙缓存",
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
