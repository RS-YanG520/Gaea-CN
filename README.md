# Gaea-CN

Gaea 2 中文**显示层**汉化工程：只翻译说明文案，不改工程文件里的类型名/属性名/枚举值。

详见 [docs/PLAN.md](docs/PLAN.md) 与 [docs/safety-rules.md](docs/safety-rules.md)。

## 可视化启动器

双击 `启动 Gaea-CN.bat`，或：

```powershell
cd D:\Projects\Gaea-CN
python tools/launcher.py
```

在窗口中选择 Gaea 安装目录（需含 `Gaea.exe`），勾选是否应用中文节点说明，点「启动 Gaea」即可。路径会记在 `config/launcher.json`。

运行日志写在 `logs/launcher.log`（窗口内可点「打开日志」）。界面钩子日志：`%LOCALAPPDATA%\Gaea-CN\startup-hook.log`。

**必须用本启动器启动 Gaea**（勾选「菜单汉化」）。直接双击官方快捷方式不会加载中文界面钩子。

若再次卡死：任务管理器结束 Gaea → 启动器里**取消勾选**菜单汉化后再开。

若写入 `Program Files` 失败，请右键「以管理员身份运行」批处理。

## 安装成「官方快捷方式即中文」（类似星空汉化）

词典已合并 `dict/xingkong/`（星空汉化社区词条，显示层专用）。不想每次开 bat 时，可把启动器装进 Gaea 目录：

```powershell
# 管理员 PowerShell
cd D:\Projects\Gaea-CN
powershell -ExecutionPolicy Bypass -File tools\install_gaea_cn.ps1
```

效果：备份 `Gaea.exe` → `Gaea.real.exe`，放入我们的启动器；之后双击原快捷方式即可。

卸载还原：

```powershell
powershell -ExecutionPolicy Bypass -File tools\install_gaea_cn.ps1 -Uninstall
```

只更新词典（不重装启动器）：

```powershell
python tools\import_xingkong_dict.py
# 再运行一次 install 脚本，或手动复制 dict 到 %LOCALAPPDATA%\Gaea-CN
```

## 命令行流程

```powershell
cd D:\Projects\Gaea-CN
python tools/extract_nodes.py
python tools/seed_sample_zh.py   # 可选：写入首批高频节点译文
python tools/build_overlay.py
powershell -ExecutionPolicy Bypass -File tools/apply_overlay.ps1
python tools/verify_terrain_roundtrip.py
```

还原原版：

```powershell
powershell -ExecutionPolicy Bypass -File tools/restore_overlay.ps1
```
