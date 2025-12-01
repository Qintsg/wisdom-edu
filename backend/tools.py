#!/usr/bin/env python
"""
自适应学习系统数据工具脚本（入口文件）

实际逻辑已拆分到 tools/ 包中，此文件仅作为 CLI 入口保持向后兼容。

使用方法：
1. 交互式菜单：python tools.py
2. 命令行参数：python tools.py <command> [options]

示例：
    python tools.py import-knowledge-map 资料/大数据图谱构建.xlsx --course-id 1
    python tools.py bootstrap-course-assets --course-name 大数据技术与应用
    python tools.py train-mefkt --course-id 72 --epochs 4 --pretrain-epochs 2
"""

from importlib import import_module
import os
from typing import Callable, cast

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wisdom_edu_api.settings')

import django
django.setup()


def _load_cli_main() -> Callable[[], None]:
    """加载真正的 CLI 入口，避免入口脚本与 tools 包同名引发静态分析混淆。"""
    cli_module = import_module('tools.cli')
    return cast(Callable[[], None], getattr(cli_module, 'main'))

if __name__ == '__main__':
    _load_cli_main()()
