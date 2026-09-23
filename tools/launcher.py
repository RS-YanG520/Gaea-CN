#!/usr/bin/env python3
"""Gaea-CN 启动器：选择安装路径后应用中文说明覆盖并启动 Gaea。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

# Allow `python tools/launcher.py` sibling imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cn_log import LOG_DIR, latest_log_path, log_exception, setup_logger

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "launcher.json"
DEFAULT_GAEA = Path(r"D:\Program Files\Gaea 2")
HOOK_DLL_CANDIDATES = (
    ROOT / "hooks" / "publish2" / "GaeaCn.StartupHook.dll",
    ROOT / "hooks" / "publish" / "GaeaCn.StartupHook.dll",
)
HOOK_DICT = ROOT / "dict" / "ui.display.zh.json"
ICON_CANDIDATES = (
    ROOT / "assets" / "Gaea-2.ico",
    DEFAULT_GAEA / "Gaea-2.ico",
)


def resolve_hook_dll() -> Path:
    for p in HOOK_DLL_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "未找到界面钩子 DLL。请运行：dotnet build hooks/GaeaCn.StartupHook -c Release -o hooks/publish2"
    )


def prepare_ui_hook() -> Path:
    """Ensure hook DLL + dictionary are ready; return absolute DLL path."""
    hook_dll = resolve_hook_dll()
    # Keep dictionary beside DLL for the hook loader
    publish_dict = hook_dll.parent / "ui.display.zh.json"
    if HOOK_DICT.is_file():
        publish_dict.write_bytes(HOOK_DICT.read_bytes())
    # Also mirror to LocalAppData fallback
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Gaea-CN"
    local.mkdir(parents=True, exist_ok=True)
    if HOOK_DICT.is_file():
        (local / "ui.display.zh.json").write_bytes(HOOK_DICT.read_bytes())
    log.info("UI hook ready: %s", hook_dll)
    return hook_dll.resolve()


# Dark tech-blue palette
C = {
    "bg": "#0b1220",
    "panel": "#111a2e",
    "panel2": "#162038",
    "border": "#1e3a5f",
    "accent": "#2dd4ff",
    "accent_dim": "#0ea5c9",
    "accent_hot": "#67e8f9",
    "text": "#e2e8f0",
    "muted": "#7dd3fc",
    "muted2": "#64748b",
    "danger": "#38bdf8",
    "entry_bg": "#0a1628",
    "btn": "#12355a",
    "btn_primary": "#0369a1",
}

log = setup_logger("launcher")


def load_config() -> dict:
    if CONFIG_PATH.is_file():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            log.debug("Loaded config from %s: %s", CONFIG_PATH, cfg)
            return cfg
        except json.JSONDecodeError as e:
            log.warning("Config JSON invalid (%s), using defaults: %s", CONFIG_PATH, e)
    defaults = {
        "gaea_root": str(DEFAULT_GAEA if DEFAULT_GAEA.is_dir() else ""),
        "apply_overlay": True,
        "ui_hook": True,
    }
    log.debug("Using default config: %s", defaults)
    return defaults


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.info("Saved config → %s", CONFIG_PATH)


def find_gaea_exe(gaea_root: Path) -> Path | None:
    candidate = gaea_root / "Gaea.exe"
    ok = candidate.is_file()
    log.debug("find_gaea_exe(%s) → %s (exists=%s)", gaea_root, candidate, ok)
    return candidate if ok else None


def resolve_icon() -> Path | None:
    for p in ICON_CANDIDATES:
        if p.is_file():
            return p
    return None


def apply_overlay(gaea_root: Path) -> None:
    """Backup once and copy overlays/Nodes.json into Resources."""
    target = gaea_root / "Resources" / "Nodes.json"
    overlay = ROOT / "overlays" / "Nodes.json"
    backup_dir = ROOT / "backups"
    backup = backup_dir / "Nodes.json.bak"

    log.info("apply_overlay start | root=%s", gaea_root)
    log.debug(
        "overlay=%s exists=%s size=%s",
        overlay,
        overlay.is_file(),
        overlay.stat().st_size if overlay.is_file() else None,
    )
    log.debug(
        "target=%s exists=%s size=%s",
        target,
        target.is_file(),
        target.stat().st_size if target.is_file() else None,
    )

    if not overlay.is_file():
        raise FileNotFoundError(
            f"未找到覆盖文件：{overlay}\n请先运行：python tools/build_overlay.py"
        )
    if not target.is_file():
        raise FileNotFoundError(f"未找到 Nodes.json：{target}\n请确认 Gaea 安装路径正确。")

    backup_dir.mkdir(parents=True, exist_ok=True)
    if not backup.is_file():
        data = target.read_bytes()
        backup.write_bytes(data)
        log.info("Created English backup (%d bytes) → %s", len(data), backup)
    else:
        log.debug("Backup already exists (%d bytes): %s", backup.stat().st_size, backup)

    data = overlay.read_bytes()
    target.write_bytes(data)
    log.info("Wrote overlay (%d bytes) → %s", len(data), target)


def restore_overlay(gaea_root: Path) -> None:
    backup = ROOT / "backups" / "Nodes.json.bak"
    target = gaea_root / "Resources" / "Nodes.json"
    log.info("restore_overlay | backup=%s target=%s", backup, target)
    if not backup.is_file():
        raise FileNotFoundError(f"没有备份文件：{backup}")
    data = backup.read_bytes()
    target.write_bytes(data)
    log.info("Restored English Nodes.json (%d bytes)", len(data))


class DarkButton(tk.Label):
    """Simple flat button that fits the dark theme (tk.Button looks dull on Win)."""

    def __init__(
        self,
        master,
        text: str,
        command,
        *,
        primary: bool = False,
        width: int | None = None,
        **kwargs,
    ):
        self._command = command
        self._primary = primary
        bg = C["btn_primary"] if primary else C["btn"]
        fg = C["text"]
        super().__init__(
            master,
            text=text,
            bg=bg,
            fg=fg,
            padx=14,
            pady=7,
            cursor="hand2",
            font=("Segoe UI", 9, "bold" if primary else "normal"),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=C["accent"] if primary else C["border"],
            highlightcolor=C["accent"],
            width=width,
            **kwargs,
        )
        self._bg = bg
        self._hover = C["accent_dim"] if primary else "#1a4a7a"
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, _e=None) -> None:
        self.configure(bg=self._hover, highlightbackground=C["accent_hot"])

    def _on_leave(self, _e=None) -> None:
        self.configure(bg=self._bg, highlightbackground=C["accent"] if self._primary else C["border"])

    def _on_click(self, _e=None) -> None:
        if self._command:
            self._command()


class LauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Gaea-CN 启动器")
        self.resizable(False, False)
        self.configure(bg=C["bg"])

        log.info("=== Launcher started | python=%s | root=%s ===", sys.version.split()[0], ROOT)

        self._set_icon()

        self.cfg = load_config()
        self.path_var = tk.StringVar(value=self.cfg.get("gaea_root", ""))
        self.apply_var = tk.BooleanVar(value=bool(self.cfg.get("apply_overlay", True)))
        self.hook_var = tk.BooleanVar(value=bool(self.cfg.get("ui_hook", True)))
        self.status_var = tk.StringVar(
            value=f"选择 Gaea 2 安装目录后点击「启动」。日志：{latest_log_path().name}"
        )

        self._build()
        self._center()
        log.debug("UI ready | path=%s apply=%s", self.path_var.get(), self.apply_var.get())

    def _set_icon(self) -> None:
        icon = resolve_icon()
        if not icon:
            log.warning("Gaea icon not found in assets/ or install dir")
            return
        try:
            self.iconbitmap(default=str(icon))
            self._icon_path = icon
            log.info("Window icon set: %s", icon)
        except tk.TclError as e:
            log.warning("Failed to set iconbitmap(%s): %s", icon, e)

    def _build(self) -> None:
        outer = tk.Frame(self, bg=C["bg"], padx=18, pady=18)
        outer.grid(row=0, column=0, sticky="nsew")

        # Header band
        header = tk.Frame(outer, bg=C["panel"], highlightthickness=1, highlightbackground=C["border"])
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header_inner = tk.Frame(header, bg=C["panel"], padx=14, pady=12)
        header_inner.pack(fill=tk.X)

        title_row = tk.Frame(header_inner, bg=C["panel"])
        title_row.pack(fill=tk.X)
        tk.Label(
            title_row,
            text="GAEA-CN",
            bg=C["panel"],
            fg=C["accent"],
            font=("Segoe UI Semibold", 16),
        ).pack(side=tk.LEFT)
        tk.Label(
            title_row,
            text="  ·  中文显示启动器",
            bg=C["panel"],
            fg=C["muted"],
            font=("Segoe UI", 10),
        ).pack(side=tk.LEFT, pady=(4, 0))

        tk.Label(
            header_inner,
            text="节点说明覆盖 + 界面显示层汉化 · 不改工程文件标识符",
            bg=C["panel"],
            fg=C["muted2"],
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(4, 0))

        # Path panel
        panel = tk.Frame(outer, bg=C["panel2"], highlightthickness=1, highlightbackground=C["border"], padx=14, pady=12)
        panel.grid(row=1, column=0, sticky="ew")

        tk.Label(
            panel,
            text="Gaea 安装路径",
            bg=C["panel2"],
            fg=C["muted"],
            font=("Segoe UI", 9),
        ).grid(row=0, column=0, sticky="w")

        row = tk.Frame(panel, bg=C["panel2"])
        row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        panel.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            row,
            textvariable=self.path_var,
            width=48,
            bg=C["entry_bg"],
            fg=C["text"],
            insertbackground=C["accent"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=C["border"],
            highlightcolor=C["accent"],
            font=("Consolas", 10),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))
        DarkButton(row, "浏览…", self.browse, width=8).pack(side=tk.LEFT)

        chk = tk.Checkbutton(
            panel,
            text="启动前应用中文节点说明（仅改 Description，不影响工程保存）",
            variable=self.apply_var,
            bg=C["panel2"],
            fg=C["text"],
            activebackground=C["panel2"],
            activeforeground=C["accent_hot"],
            selectcolor=C["entry_bg"],
            highlightthickness=0,
            font=("Segoe UI", 9),
            cursor="hand2",
        )
        chk.grid(row=2, column=0, sticky="w", pady=(12, 0))

        chk2 = tk.Checkbutton(
            panel,
            text="启用菜单汉化（安全版：仅弹层翻译，勿用旧版全屏扫描）",
            variable=self.hook_var,
            bg=C["panel2"],
            fg=C["text"],
            activebackground=C["panel2"],
            activeforeground=C["accent_hot"],
            selectcolor=C["entry_bg"],
            highlightthickness=0,
            font=("Segoe UI", 9),
            cursor="hand2",
        )
        chk2.grid(row=3, column=0, sticky="w", pady=(6, 0))

        # Actions
        btns = tk.Frame(outer, bg=C["bg"])
        btns.grid(row=2, column=0, sticky="e", pady=(14, 0))
        DarkButton(btns, "打开日志", self.open_log).pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(btns, "还原英文说明", self.restore).pack(side=tk.LEFT, padx=(0, 8))
        DarkButton(btns, "启动 Gaea", self.launch, primary=True).pack(side=tk.LEFT)

        # Status
        status = tk.Label(
            outer,
            textvariable=self.status_var,
            bg=C["bg"],
            fg=C["muted2"],
            font=("Segoe UI", 8),
            wraplength=500,
            justify="left",
            anchor="w",
        )
        status.grid(row=3, column=0, sticky="ew", pady=(14, 0))

        # Bottom accent line
        tk.Frame(outer, bg=C["accent_dim"], height=2).grid(row=4, column=0, sticky="ew", pady=(14, 0))

        self.bind("<Return>", lambda _e: self.launch())

    def _center(self) -> None:
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 3
        self.geometry(f"{w}x{h}+{x}+{y}")

    def browse(self) -> None:
        initial = self.path_var.get().strip() or str(Path.home())
        log.debug("Browse dialog initialdir=%s", initial)
        chosen = filedialog.askdirectory(title="选择 Gaea 2 安装目录", initialdir=initial)
        if chosen:
            self.path_var.set(chosen)
            log.info("User selected path: %s", chosen)
        else:
            log.debug("Browse cancelled")

    def open_log(self) -> None:
        path = latest_log_path()
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            path.write_text("", encoding="utf-8")
        log.info("Opening log file: %s", path)
        try:
            if sys.platform == "win32":
                os.startfile(str(path))  # type: ignore[attr-defined]
            else:
                subprocess.Popen(["xdg-open", str(path)])
        except OSError as e:
            log_exception(log, "Failed to open log")
            messagebox.showerror("失败", f"无法打开日志：\n{path}\n{e}")

    def _validated_root(self) -> Path | None:
        raw = self.path_var.get().strip().strip('"')
        if not raw:
            log.warning("Validation failed: empty path")
            messagebox.showwarning("提示", "请先选择 Gaea 安装路径。")
            return None
        root = Path(raw)
        if not root.is_dir():
            log.warning("Validation failed: not a directory: %s", root)
            messagebox.showerror("错误", f"目录不存在：\n{root}")
            return None
        if not find_gaea_exe(root):
            log.warning("Validation failed: Gaea.exe missing under %s", root)
            messagebox.showerror("错误", f"未在该目录找到 Gaea.exe：\n{root}")
            return None
        log.debug("Validated root: %s", root)
        return root

    def restore(self) -> None:
        root = self._validated_root()
        if not root:
            return
        try:
            restore_overlay(root)
            self.status_var.set("已还原英文 Nodes.json。")
            messagebox.showinfo("完成", "已还原为英文节点说明。")
        except FileNotFoundError as e:
            log.error("%s", e)
            messagebox.showerror("错误", str(e))
        except OSError as e:
            log_exception(log, "Restore failed")
            messagebox.showerror("失败", f"还原失败（可能需要管理员权限）：\n{e}")

    def launch(self) -> None:
        root = self._validated_root()
        if not root:
            return

        self.cfg["gaea_root"] = str(root)
        self.cfg["apply_overlay"] = bool(self.apply_var.get())
        self.cfg["ui_hook"] = bool(self.hook_var.get())
        save_config(self.cfg)
        log.info(
            "Launch requested | root=%s apply_overlay=%s ui_hook=%s",
            root,
            self.apply_var.get(),
            self.hook_var.get(),
        )

        try:
            if self.apply_var.get():
                self.status_var.set("正在应用中文说明…")
                self.update_idletasks()
                apply_overlay(root)
                self.status_var.set("中文说明已应用，正在启动…")
            else:
                log.info("Skipping overlay apply (checkbox off)")
                self.status_var.set("正在启动…")
            self.update_idletasks()

            exe = find_gaea_exe(root)
            assert exe is not None

            env = os.environ.copy()
            if self.hook_var.get():
                hook = prepare_ui_hook()
                # Chain with any existing hooks
                prev = env.get("DOTNET_STARTUP_HOOKS", "").strip()
                env["DOTNET_STARTUP_HOOKS"] = (
                    f"{hook}{os.pathsep}{prev}" if prev else str(hook)
                )
                log.info("DOTNET_STARTUP_HOOKS=%s", env["DOTNET_STARTUP_HOOKS"])
            else:
                env.pop("DOTNET_STARTUP_HOOKS", None)
                log.info("UI hook disabled")

            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
            proc = subprocess.Popen(
                [str(exe)],
                cwd=str(root),
                env=env,
                close_fds=True,
                creationflags=creationflags,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            log.info("Started Gaea.exe pid=%s path=%s cwd=%s", proc.pid, exe, root)
            self.status_var.set(f"已启动：{exe}（日志 {latest_log_path().name}）")
            self.after(400, self.destroy)
        except OSError as e:
            log_exception(log, "Launch/apply OSError")
            messagebox.showerror(
                "失败",
                f"操作失败（写入 Program Files 可能需要管理员权限）：\n{e}\n\n详见日志：\n{latest_log_path()}",
            )
            self.status_var.set("启动失败，请查看日志。")
        except FileNotFoundError as e:
            log.error("%s", e)
            messagebox.showerror("失败", f"{e}\n\n详见日志：\n{latest_log_path()}")
            self.status_var.set("启动失败，请查看日志。")
        except Exception:
            log_exception(log, "Unexpected launch failure")
            messagebox.showerror("失败", f"未预期错误，请查看日志：\n{latest_log_path()}")
            self.status_var.set("启动失败，请查看日志。")


def main() -> None:
    try:
        app = LauncherApp()
        try:
            app.call("tk", "scaling", 1.25)
        except tk.TclError:
            pass
        app.mainloop()
        log.info("=== Launcher closed ===")
    except Exception:
        log_exception(log, "Launcher crashed before/during mainloop")
        raise


if __name__ == "__main__":
    main()
