#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
命令行入口门面。

交互式菜单与 argparse 分发已拆到独立模块，当前文件保留 `tools.cli`
对外入口，避免旧脚本和 `tools.__init__` 导入路径失效。
"""

from __future__ import annotations

import argparse

from tools.cli_menu import show_menu
from tools.cli_parser import build_parser, dispatch_command


# 维护意图：兼容旧的内部分发函数名
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _dispatch_command(args: argparse.Namespace) -> None:
    """兼容旧的内部分发函数名。"""
    dispatch_command(args)


# 维护意图：CLI 统一入口
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def main() -> None:
    """CLI 统一入口。"""
    parser = build_parser()
    args = parser.parse_args()

    if not args.cmd:
        show_menu()
        return

    dispatch_command(args)


__all__ = ["build_parser", "dispatch_command", "main", "show_menu", "_dispatch_command"]
