#!/usr/bin/env python3
"""Merge Options-dialog strings into ui.display.zh.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "dict" / "ui.display.zh.json"

ADD = {
    # Window chrome
    "Options": "选项",
    "Reset this page": "重置本页",
    "Accept Changes": "接受更改",
    "Cancel": "取消",
    # Sidebar
    "General": "常规",
    "Paths": "路径",
    "Toolbox": "工具箱",
    "Data View": "数据视图",
    "Cache": "缓存",
    "Navigation": "导航",
    "Lazy Menu": "快捷菜单",
    "Compute": "计算",
    "Experimental": "实验性",
    # General
    "Start Gaea on": "启动 Gaea 于",
    "Monitor 0 (Primary)": "显示器 0（主显示器）",
    "Check for updates on startup": "启动时检查更新",
    "Move cursor to target when using the Lazy Menu": "使用快捷菜单时将光标移到目标",
    "Show Expert Tools": "显示专家工具",
    "Enable Verbose Logging": "启用详细日志",
    "Report crash reports anonymously": "匿名发送崩溃报告",
    "Report anonymous usage statistics": "匿名发送使用统计",
    "Show warning for orphan variables": "对孤立变量显示警告",
    "Local License Server": "本地许可证服务器",
    "Use Web Proxy": "使用 Web 代理",
    "Open Data Folder": "打开数据文件夹",
    "Run Diagnostics": "运行诊断",
    "Factory Reset": "恢复出厂设置",
    # Paths
    "File Thumbnails": "文件缩略图",
    "Don't Save": "不保存",
    "Central Data Folder": "中央数据文件夹",
    "Next to File": "文件旁",
    "User Files Path": "用户文件路径",
    "This is where all Presets, Screenshots, and other Gaea documents are stored.": "此处存放预设、截图及其他 Gaea 文档。",
    "Project Files Path": "工程文件路径",
    "The is where all Gaea project files are stored by default.": "默认存放所有 Gaea 工程文件的位置。",
    "TIPS": "提示",
    # Toolbox
    "Configuration": "配置",
    "Menus": "菜单",
    "Layout": "布局",
    "Large": "大",
    "Compact": "紧凑",
    "Buttons": "按钮",
    "Organization": "组织方式",
    "Nested by Family": "按族嵌套",
    "Show All": "显示全部",
    "Show icons in Toolbox": "在工具箱中显示图标",
    "Highlight most-used nodes": "高亮常用节点",
    "Pin most-used nodes": "固定常用节点",
    "Search": "搜索",
    "Show Family Name": "显示族名称",
    "Show Icons": "显示图标",
    "Maximum Result": "最大结果数",
    "Show SatMaps List as a Single Stack": "将 SatMaps 列表显示为单栈",
    # Graph
    "Grid Snap Size": "网格吸附大小",
    "Allow node shortcuts only when cursor is inside the graph": "仅当光标在节点图内时允许节点快捷键",
    "Hide Graph Tabs": "隐藏节点图标签",
    "Hide Bookmark Shortcuts": "隐藏书签快捷键",
    "Record Graph Movements and Zoom in Undos": "在撤销中记录节点图平移与缩放",
    # Node
    "Node Style": "节点样式",
    "Muted (Gaea 2)": "柔和（Gaea 2）",
    "Vibrant (Gaea 1)": "鲜明（Gaea 1）",
    "Show shine effect on Node when build completes": "构建完成时在节点上显示光泽效果",
    "Show build time on node": "在节点上显示构建时间",
    "Show values with high precision": "以高精度显示数值",
    "Accept values when clicking outside of editable field": "点击可编辑字段外时接受数值",
    "Use slider for Seed instead of new Seed control": "用滑块代替新的种子控件",
    "Snap connections to available ports": "吸附连接到可用端口",
    "Double-click on tip to connect": "双击端口以连接",
    "Double-click on port to connect": "双击端口以连接",
    "Gaea 1 Style Mask Ports": "Gaea 1 风格遮罩端口",
    # Data View
    "Icons": "图标",
    "Colorful": "彩色",
    "Muted": "柔和",
    "Hide": "隐藏",
    "Always expand": "始终展开",
    # Build
    "Default File Formats": "默认文件格式",
    "Build Output": "构建输出",
    "This is where output files from builds are stored. It is denoted by the <Builds> token in Build Settings > Destination.": "构建输出文件存放于此。在「构建设置 > 目标」中用 <Builds> 标记表示。",
    "Heightfield": "高度场",
    "Color Maps": "颜色贴图",
    "Masks": "遮罩",
    "Remove Primary port name in Build output": "构建输出中移除主端口名",
    "Purge unnecessary cache during build to conserve memory.": "构建时清理不必要的缓存以节省内存。",
    "Timeout for Gaea Server": "Gaea 服务器超时",
    "minutes": "分钟",
    # Cache
    "Logs and Autosaves": "日志与自动保存",
    "Delete after 45 days": "45 天后删除",
    "Always Cache to Disk on Close": "关闭时始终缓存到磁盘",
    "Smart Cache": "智能缓存",
    "Use Smart Cache": "使用智能缓存",
    "Idle Threshold": "空闲阈值",
    "Cache Output": "缓存输出",
    "Smart Cache and Cache to Disk": "智能缓存并缓存到磁盘",
    "Cache Locations": "缓存位置",
    "Baked Cache": "烘焙缓存",
    "2K or 4K cache is offloaded from RAM to disk when idle for the given duration. This is recommended when using SSD storage.": "空闲达到设定时间后，将 2K/4K 缓存从内存卸载到磁盘。建议在使用 SSD 时开启。",
    # Viewport
    "Antialiasing": "抗锯齿",
    "Background": "背景",
    "Mask Gradient": "遮罩渐变",
    "Gizmos": "小工具",
    "None": "无",
    "Greyscale": "灰度",
    "Hot": "热力",
    "Red": "红",
    "Blue": "蓝",
    "Spectrum": "光谱",
    "Do not clear viewport when unselecting a node": "取消选择节点时不清除视口",
    "Show Grid": "显示网格",
    "Show Compass": "显示罗盘",
    "Show Base Marker": "显示基准标记",
    "Conserve memory when displaying 4K terrains": "显示 4K 地形时节省内存",
    "2D Viewport": "二维视口",
    "3D + 2D Viewport": "三维+二维视口",
    # Navigation
    "Mouse Navigation": "鼠标导航",
    "Mouse Button": "鼠标按键",
    "Hold Alt": "按住 Alt",
    "Sensitivity": "灵敏度",
    "Rotate": "旋转",
    "Pan": "平移",
    "Zoom": "缩放",
    "Left": "左键",
    "Middle": "中键",
    "Right": "右键",
    "Invert Y axis": "反转 Y 轴",
    "Flip Y Pan Direction for QE keys": "翻转 QE 键的 Y 向平移方向",
    "When disabled, Q pans up, E pans down. When enabled, the direction is reversed.": "关闭时：Q 上移，E 下移；开启后方向相反。",
    "Invert zoom direction": "反转缩放方向",
    "Show viewport navigation hint for 10 seconds when Gaea starts": "启动 Gaea 时显示 10 秒视口导航提示",
    # Lazy Menu
    "Lighting Options": "光照选项",
    "Properties": "属性",
    "Modifiers": "修改器",
    "Node Tree": "节点树",
    "Variables View": "变量视图",
    "Build View": "构建视图",
    "Build Settings": "构建设置",
    "Bright": "明亮",
    # Compute
    "Available Devices": "可用设备",
    "Native": "原生",
    "CUDA": "CUDA",
    "Scan Hardware and Determine Speeds": "扫描硬件并测定速度",
    "Enforce Optimal Settings": "强制最优设置",
    # Experimental
    "Preview Options": "预览选项",
    "Compact Interface": "紧凑界面",
    "Use old memory optimization": "使用旧内存优化",
    "Restart to take effect.": "重启后生效。",
    "Disable UI animations": "禁用界面动画",
    "Use new Auto Layout method": "使用新自动布局方法",
    "Use Adaptive Debounce for Smoother Node Updates": "使用自适应防抖以平滑节点更新",
    "Populate Recent List in Start Experience": "在开始界面填充最近列表",
    "Custom Locations to show in File Dialogs (one per line)": "文件对话框中显示的自定义位置（每行一个）",
    "Show only these locations": "仅显示这些位置",
}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    data.update(ADD)
    extra = {}
    for k, v in list(data.items()):
        if k.endswith("..."):
            extra[k[:-3] + "…"] = v
    data.update(extra)
    PATH.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {PATH} size={len(data)}")


if __name__ == "__main__":
    main()
