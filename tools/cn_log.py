#!/usr/bin/env python3
"""Shared logging for Gaea-CN tools. Logs live under <repo>/logs/ for easy debugging."""

from __future__ import annotations

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"

_configured: set[str] = set()


def setup_logger(name: str = "gaea_cn", filename: str | None = None) -> logging.Logger:
    """Configure a logger that writes to logs/<name>.log and stderr.

    Safe to call multiple times; handlers are only attached once per name.
    """
    log = logging.getLogger(name)
    if name in _configured:
        return log

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / (filename or f"{name}.log")

    log.setLevel(logging.DEBUG)
    log.propagate = False

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = RotatingFileHandler(
        log_path,
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    log.addHandler(fh)

    sh = logging.StreamHandler(sys.stderr)
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)
    log.addHandler(sh)

    _configured.add(name)
    log.debug("Logger ready → %s", log_path)
    return log


def log_exception(log: logging.Logger, msg: str = "Unhandled exception") -> None:
    log.error("%s\n%s", msg, traceback.format_exc())


def latest_log_path(name: str = "launcher") -> Path:
    return LOG_DIR / f"{name}.log"
